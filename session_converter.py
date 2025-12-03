#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telentro Session Dönüştürücü Modülü
Python session'larını C# formatına dönüştürme
"""

import os
import json
import pickle
import sqlite3
import struct
import base64
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import telethon
from telethon import TelegramClient

@dataclass
class SessionInfo:
    """Session bilgisi"""
    session_name: str
    session_type: str  # 'telethon', 'pyrogram', 'pytdbot', 'wTelegram'
    api_id: int
    api_hash: str
    phone: Optional[str] = None
    user_id: Optional[int] = None
    dc_id: Optional[int] = None
    created_at: Optional[datetime] = None
    file_size: int = 0
    is_valid: bool = False

class SessionConverter:
    """Session dönüştürücü sınıfı"""
    
    def __init__(self, output_dir: str = "converted_sessions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # C# session formatı için şablonlar
        self.csharp_template = '''using System;
using System.IO;
using System.Threading.Tasks;
using Telegram.Client;
using Telegram.Entities;

namespace Telegram.Sessions
{{
    public class {session_class}
    {{
        public static SessionData GetSessionData()
        {{
            return new SessionData
            {{
                ApiId = {api_id},
                ApiHash = "{api_hash}",
                SessionString = "{session_string}",
                UserId = {user_id},
                DcId = {dc_id},
                PhoneNumber = "{phone}",
                CreatedAt = DateTime.Parse("{created_at}")
            }};
        }}
        
        public static async Task<TelegramClient> CreateClient()
        {{
            var sessionData = GetSessionData();
            var client = new TelegramClient(sessionData);
            await client.ConnectAsync();
            return client;
        }}
    }}
}}'''

        self.json_template = {{
            "api_id": 0,
            "api_hash": "",
            "session_string": "",
            "user_id": 0,
            "dc_id": 0,
            "phone": "",
            "created_at": "",
            "version": "1.0",
            "converter": "Telentro Session Converter"
        }}
    
    def detect_session_type(self, session_path: str) -> str:
        """Session tipini tespit et"""
        path = Path(session_path)
        
        if not path.exists():
            return "unknown"
        
        # Dosya uzantısına göre
        if path.suffix == '.session':
            # İçerik kontrolü
            try:
                with open(path, 'rb') as f:
                    header = f.read(16)
                    
                # Telethon session formatı
                if b'TG_SESSION' in header[:16]:
                    return 'telethon'
                # Pyrogram session formatı
                elif header.startswith(b'\x08'):
                    return 'pyrogram'
                else:
                    return 'telethon'  # Varsayılan
                    
            except Exception:
                return 'telethon'
        
        elif path.suffix == '.tdb':
            return 'pytdbot'
        elif path.suffix == '.wdb':
            return 'wtelegram'
        elif path.is_dir():
            return 'tdata'
        else:
            return 'unknown'
    
    def extract_telethon_session(self, session_path: str) -> Dict:
        """Telethon session'ından veri çıkar"""
        try:
            # Session bilgilerini almak için geçici client oluştur
            session_name = Path(session_path).stem
            
            # .env dosyasından API bilgilerini oku
            api_id, api_hash = self._get_api_credentials()
            
            if not api_id or not api_hash:
                raise ValueError("API credentials not found in .env file")
            
            client = TelegramClient(session_path, api_id, api_hash)
            
            # Session verilerini çıkar
            session_data = {
                'session_name': session_name,
                'session_type': 'telethon',
                'api_id': api_id,
                'api_hash': api_hash,
                'session_string': self._encode_session_file(session_path),
                'file_size': os.path.getsize(session_path),
                'created_at': datetime.now().isoformat()
            }
            
            # Kullanıcı bilgilerini al (eğer bağlanabilirse)
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def get_user_info():
                    await client.connect()
                    if await client.is_user_authorized():
                        me = await client.get_me()
                        session_data.update({
                            'user_id': me.id,
                            'phone': me.phone,
                            'dc_id': me.dc_id if hasattr(me, 'dc_id') else None,
                            'is_valid': True
                        })
                    await client.disconnect()
                
                loop.run_until_complete(get_user_info())
                loop.close()
                
            except Exception as e:
                self.logger.warning(f"User info extraction failed: {e}")
                session_data['is_valid'] = False
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Telethon session extraction failed: {e}")
            return {}
    
    def extract_pyrogram_session(self, session_path: str) -> Dict:
        """Pyrogram session'ından veri çıkar"""
        try:
            session_name = Path(session_path).stem
            
            # Pyrogram session formatı
            with open(session_path, 'rb') as f:
                session_data_raw = f.read()
            
            # Session'ı decode et
            session_string = base64.b64encode(session_data_raw).decode('utf-8')
            
            return {
                'session_name': session_name,
                'session_type': 'pyrogram',
                'session_string': session_string,
                'file_size': os.path.getsize(session_path),
                'created_at': datetime.now().isoformat(),
                'is_valid': False  # Pyrogram için API bilgileri gerekli
            }
            
        except Exception as e:
            self.logger.error(f"Pyrogram session extraction failed: {e}")
            return {}
    
    def extract_tdata_folder(self, tdata_path: str) -> List[Dict]:
        """TData klasöründen session'ları çıkar"""
        sessions = []
        tdata_dir = Path(tdata_path)
        
        if not tdata_dir.is_dir():
            self.logger.error(f"TData path is not a directory: {tdata_path}")
            return sessions
        
        try:
            # TData içindeki dosyaları tara
            for file_path in tdata_dir.glob('**/*'):
                if file_path.is_file() and file_path.suffix in ['.tdb', '.wdb']:
                    session_data = {
                        'session_name': file_path.stem,
                        'session_type': 'tdata',
                        'file_path': str(file_path),
                        'file_size': file_path.stat().st_size,
                        'created_at': datetime.now().isoformat(),
                        'is_valid': False
                    }
                    sessions.append(session_data)
            
            # TData klasörünü kopyala
            tdata_backup = self.output_dir / f"tdata_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(tdata_dir, tdata_backup)
            
            self.logger.info(f"TData folder copied to: {tdata_backup}")
            
        except Exception as e:
            self.logger.error(f"TData extraction failed: {e}")
        
        return sessions
    
    def convert_to_csharp(self, session_data: Dict) -> str:
        """Session verisini C# koduna dönüştür"""
        session_class = f"Session_{session_data['session_name'].replace('.', '_').replace('-', '_')}"
        
        csharp_code = self.csharp_template.format(
            session_class=session_class,
            api_id=session_data.get('api_id', 0),
            api_hash=session_data.get('api_hash', ''),
            session_string=session_data.get('session_string', ''),
            user_id=session_data.get('user_id', 0),
            dc_id=session_data.get('dc_id', 0),
            phone=session_data.get('phone', ''),
            created_at=session_data.get('created_at', datetime.now().isoformat())
        )
        
        return csharp_code
    
    def convert_to_json(self, session_data: Dict) -> Dict:
        """Session verisini JSON formatına dönüştür"""
        json_data = self.json_template.copy()
        json_data.update(session_data)
        return json_data
    
    def convert_to_session_string(self, session_path: str) -> str:
        """Session dosyasını session string'e dönüştür"""
        try:
            with open(session_path, 'rb') as f:
                session_bytes = f.read()
            
            # Base64 encode
            session_string = base64.b64encode(session_bytes).decode('utf-8')
            return session_string
            
        except Exception as e:
            self.logger.error(f"Session string conversion failed: {e}")
            return ""
    
    def save_converted_session(self, session_data: Dict, format_type: str = 'json') -> str:
        """Dönüştürülmüş session'ı kaydet"""
        session_name = session_data['session_name']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'csharp':
            filename = f"{session_name}_{timestamp}.cs"
            filepath = self.output_dir / filename
            
            csharp_code = self.convert_to_csharp(session_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(csharp_code)
                
        elif format_type == 'json':
            filename = f"{session_name}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            json_data = self.convert_to_json(session_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
                
        elif format_type == 'session_string':
            filename = f"{session_name}_{timestamp}.txt"
            filepath = self.output_dir / filename
            
            session_string = session_data.get('session_string', '')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(session_string)
        
        self.logger.info(f"Session saved as {format_type}: {filepath}")
        return str(filepath)
    
    def convert_directory(self, input_dir: str, output_format: str = 'json') -> List[str]:
        """Dizindeki tüm session'ları dönüştür"""
        input_path = Path(input_dir)
        converted_files = []
        
        if not input_path.exists():
            self.logger.error(f"Input directory not found: {input_dir}")
            return converted_files
        
        try:
            if input_path.is_dir():
                # TData klasörü mü?
                if input_path.name == 'tdata' or any(input_path.glob('*.tdb')):
                    sessions = self.extract_tdata_folder(str(input_path))
                    for session in sessions:
                        filepath = self.save_converted_session(session, output_format)
                        converted_files.append(filepath)
                
                # Normal session dosyaları
                else:
                    for session_file in input_path.glob('*.session'):
                        session_type = self.detect_session_type(str(session_file))
                        
                        if session_type == 'telethon':
                            session_data = self.extract_telethon_session(str(session_file))
                        elif session_type == 'pyrogram':
                            session_data = self.extract_pyrogram_session(str(session_file))
                        else:
                            continue
                        
                        if session_data:
                            filepath = self.save_converted_session(session_data, output_format)
                            converted_files.append(filepath)
            
            elif input_path.is_file():
                # Tek dosya
                session_type = self.detect_session_type(str(input_path))
                
                if session_type == 'telethon':
                    session_data = self.extract_telethon_session(str(input_path))
                elif session_type == 'pyrogram':
                    session_data = self.extract_pyrogram_session(str(input_path))
                else:
                    self.logger.error(f"Unsupported session type: {session_type}")
                    return converted_files
                
                if session_data:
                    filepath = self.save_converted_session(session_data, output_format)
                    converted_files.append(filepath)
        
        except Exception as e:
            self.logger.error(f"Directory conversion failed: {e}")
        
        return converted_files
    
    def _encode_session_file(self, session_path: str) -> str:
        """Session dosyasını encode et"""
        return self.convert_to_session_string(session_path)
    
    def _get_api_credentials(self) -> tuple:
        """.env dosyasından API bilgilerini al"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_id = os.getenv('TELEGRAM_API_ID')
            api_hash = os.getenv('TELEGRAM_API_HASH')
            
            return api_id, api_hash
            
        except Exception:
            return None, None
    
    def get_conversion_report(self) -> Dict:
        """Dönüştürme raporu"""
        converted_files = list(self.output_dir.glob('*'))
        
        report = {
            'total_converted': len(converted_files),
            'conversion_date': datetime.now().isoformat(),
            'output_directory': str(self.output_dir),
            'files_by_type': {},
            'files': []
        }
        
        for file_path in converted_files:
            if file_path.is_file():
                file_info = {
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'type': file_path.suffix,
                    'created': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                }
                report['files'].append(file_info)
                
                file_type = file_path.suffix
                report['files_by_type'][file_type] = report['files_by_type'].get(file_type, 0) + 1
        
        return report

# Kullanım örneği
def example_usage():
    """Kullanım örneği"""
    converter = SessionConverter()
    
    # Tek session dosyasını dönüştür
    converted = converter.convert_directory('my_session.session', 'json')
    print(f"Converted files: {converted}")
    
    # Tüm session'ları dönüştür
    all_converted = converter.convert_directory('./sessions', 'csharp')
    print(f"All converted files: {all_converted}")
    
    # Rapor al
    report = converter.get_conversion_report()
    print("Conversion report:", report)

if __name__ == "__main__":
    example_usage()
