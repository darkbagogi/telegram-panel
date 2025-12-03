#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Servis Modülü
Web panel için Telegram işlemlerini yönetir
"""

import os
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import User, Channel, Chat
from dotenv import load_dotenv

load_dotenv()

class TelegramService:
    """Telegram işlemleri için servis sınıfı"""
    
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.client = None
        self._connected = False
    
    async def connect(self):
        """Telegram'a bağlan"""
        if not self.api_id or not self.api_hash or not self.phone:
            raise ValueError("Telegram API bilgileri eksik")
        
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        self._connected = True
        return True
    
    async def disconnect(self):
        """Bağlantıyı kes"""
        if self.client:
            await self.client.disconnect()
            self._connected = False
    
    def is_connected(self):
        """Bağlantı durumunu kontrol et"""
        return self._connected and self.client and self.client.is_connected()
    
    async def get_user_groups(self) -> List[Dict]:
        """Kullanıcının gruplarını getir"""
        if not self.is_connected():
            await self.connect()
        
        dialogs = await self.client.get_dialogs()
        groups = []
        
        for dialog in dialogs:
            if isinstance(dialog.entity, (Channel, Chat)):
                groups.append({
                    'id': dialog.entity.id,
                    'title': dialog.entity.title,
                    'username': getattr(dialog.entity, 'username', None),
                    'members_count': getattr(dialog.entity, 'participants_count', 0),
                    'type': 'channel' if isinstance(dialog.entity, Channel) else 'chat'
                })
        
        return groups
    
    async def get_group_members(self, group_identifier: str) -> List[Dict]:
        """Belirtilen gruptan üyeleri çek"""
        if not self.is_connected():
            await self.connect()
        
        try:
            group = await self.client.get_entity(group_identifier)
            members = await self.client.get_participants(group, limit=None)
            
            member_list = []
            for member in members:
                if isinstance(member, User):
                    member_list.append({
                        'id': member.id,
                        'username': member.username,
                        'first_name': member.first_name,
                        'last_name': member.last_name,
                        'phone': member.phone,
                        'is_bot': member.bot,
                        'is_verified': member.verified,
                        'is_premium': getattr(member, 'premium', False)
                    })
            
            return member_list
        except Exception as e:
            raise Exception(f"Üyeler çekilirken hata: {str(e)}")
    
    async def transfer_members(self, source_group: str, target_group: str, 
                              member_ids: List[int], max_members: int = 50) -> Dict:
        """Üyeleri hedef gruba aktar"""
        if not self.is_connected():
            await self.connect()
        
        try:
            target = await self.client.get_entity(target_group)
            
            results = {
                'success': [],
                'failed': [],
                'total': min(len(member_ids), max_members)
            }
            
            for i, member_id in enumerate(member_ids[:max_members]):
                try:
                    user = await self.client.get_entity(member_id)
                    await self.client(InviteToChannelRequest(target, [user]))
                    
                    results['success'].append({
                        'user_id': member_id,
                        'username': user.username,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Spam koruması için bekleme
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    results['failed'].append({
                        'user_id': member_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"Aktarım sırasında hata: {str(e)}")
    
    async def save_members_to_file(self, members: List[Dict], filename: str):
        """Üyeleri dosyaya kaydet"""
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(members, f, ensure_ascii=False, indent=4)
        
        return filepath

# Global servis instance
telegram_service = TelegramService()
