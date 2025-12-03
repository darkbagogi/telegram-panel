#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telentro Grup Bulucu Modülü
Anahtar kelimeye göre grup arama ve keşfetme
"""

import asyncio
import random
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors import FloodWaitError, ChatAdminRequiredError

@dataclass
class GroupInfo:
    """Grup bilgisi"""
    id: int
    title: str
    username: str
    members_count: int
    description: str
    is_verified: bool
    is_scam: bool
    is_restricted: bool
    date: datetime
    language: str = "unknown"

class GroupFinder:
    """Grup bulucu sınıfı"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.found_groups = []
        self.search_keywords = {
            'tr': ['yazılım', 'teknoloji', 'iş', 'girişim', 'startup', 'yapay zeka', 
                   'blockchain', 'kripto', 'pazarlama', 'ticaret', 'e-ticaret'],
            'en': ['technology', 'business', 'startup', 'ai', 'blockchain', 'crypto', 
                   'marketing', 'trade', 'ecommerce', 'software'],
            'ru': ['технологии', 'бизнес', 'стартап', 'искусственный интеллект', 
                   'блокчейн', 'крипто', 'маркетинг', 'торговля'],
            'ar': ['تقنية', 'أعمال', 'بدء', 'ذكاء اصطناعي', 'بلوكشين', 'تشفير', 'تسويق'],
            'es': ['tecnología', 'negocios', 'startup', 'ia', 'blockchain', 'cripto', 
                   'marketing', 'comercio'],
            'fr': ['technologie', 'entreprise', 'startup', 'ia', 'blockchain', 'crypto', 
                   'marketing', 'commerce'],
            'de': ['technologie', 'geschäft', 'startup', 'ki', 'blockchain', 'krypto', 
                   'marketing', 'handel'],
            'it': ['tecnologia', 'affari', 'startup', 'ia', 'blockchain', 'cripto', 
                   'marketing', 'commercio'],
            'pt': ['tecnologia', 'negócios', 'startup', 'ia', 'blockchain', 'cripto', 
                   'marketing', 'comércio'],
            'hi': ['तकनीक', 'व्यवसाय', 'स्टार्टअप', 'आई', 'ब्लॉकचेन', 'क्रिप्टो', 'मार्केटिंग'],
            'zh': ['技术', '商业', '初创', '人工智能', '区块链', '加密', '营销'],
            'ja': ['技術', 'ビジネス', 'スタートアップ', 'AI', 'ブロックチェーン', '暗号', 'マーケティング'],
            'ko': ['기술', '비즈니스', '스타트업', 'AI', '블록체인', '암호', '마케팅'],
            'fa': ['فناوری', 'تجارت', 'استارتاپ', 'هوش مصنوعی', 'بلاکچین', 'رمز', 'بازاریابی'],
            'ur': ['ٹیکنالوجی', 'کاروبار', 'اسٹارٹ اپ', 'ای آئی', 'بلوک چین', 'کرپٹو', 'مارکیٹنگ'],
            'bn': ['প্রযুক্তি', 'ব্যবসা', 'স্টার্টআপ', 'এআই', 'ব্লকচেইন', 'ক্রিপ্টো', 'মার্কেটিং'],
            'ta': ['தொழில்நுட்பம்', 'வணிகம்', 'தொடக்கம்', 'செயற்கை நுண்ணறிவு', 'பிளாக்செயின்', 'கிரிப்டோ', 'சந்தைப்படுத்தல்'],
            'te': ['టెక్నాలజీ', 'వ్యాపారం', 'స్టార్టప్', 'ఏఐ', 'బ్లాక్‌చెయిన్', 'క్రిప్టో', 'మార్కెటింగ్'],
            'ml': ['ടെക്നോളജി', 'ബിസിനസ്', 'സ്റ്റാർട്ടപ്പ്', 'എഐ', 'ബ്ലോക്ക്ചെയിൻ', 'ക്രിപ്റ്റോ', 'മാർക്കറ്റിംഗ്'],
            'kn': ['ತಂತ್ರಜ್ಞಾನ', 'ವ್ಯಾಪಾರ', 'ಸ್ಟಾರ್ಟಪ್', 'ಏಐ', 'ಬ್ಲಾಕ್‌ಚೈನ್', 'ಕ್ರಿಪ್ಟೋ', 'ಮಾರ್ಕೆಟಿಂಗ್'],
            'gu': ['ટેકનોલોજી', 'બિઝનેસ', 'સ્ટાર્ટઅપ', 'એઆઈ', 'બ્લોકચેન', 'ક્રિપ્ટો', 'માર્કેટિંગ'],
            'pa': ['ਤਕਨਾਲਜੀ', 'ਬਿਜ਼ਨਸ', 'ਸਟਾਰਟਅਪ', 'ਏਆਈ', 'ਬਲਾਕਚੇਨ', 'ਕ੍ਰਿਪਟੋ', 'ਮਾਰਕੀਟਿੰਗ'],
            'or': ['ଟେକନୋଲୋଜି', 'ବ୍ୟବସାୟ', 'ସ୍ଟାର୍ଟଅପ୍', 'ଏଆଇ', 'ବ୍ଲକଚେନ୍', 'କ୍ରିପ୍ଟୋ', 'ମାର୍କେଟିଂ'],
            'as': ['প্ৰযুক্তি', 'ব্যৱসায়', 'ষ্টাৰ্টআপ', 'এআই', 'ব্লকচেইন', 'ক্ৰিপ্টো', 'মাৰ্কেটিং']
        }
    
    async def search_groups_by_keyword(self, keyword: str, limit: int = 50) -> List[GroupInfo]:
        """Anahtar kelimeye göre grup ara"""
        try:
            self.logger.info(f"'{keyword}' anahtar kelimesi ile grup arama başlatıldı")
            
            results = await self.client(SearchRequest(
                q=keyword,
                limit=limit,
                peer=InputPeerEmpty()
            ))
            
            groups = []
            for chat in results.chats:
                if hasattr(chat, 'megagroup') and chat.megagroup:
                    group_info = GroupInfo(
                        id=chat.id,
                        title=getattr(chat, 'title', ''),
                        username=getattr(chat, 'username', ''),
                        members_count=getattr(chat, 'participants_count', 0),
                        description=getattr(chat, 'about', ''),
                        is_verified=getattr(chat, 'verified', False),
                        is_scam=getattr(chat, 'scam', False),
                        is_restricted=getattr(chat, 'restricted', False),
                        date=getattr(chat, 'date', datetime.now())
                    )
                    groups.append(group_info)
            
            self.found_groups.extend(groups)
            self.logger.info(f"{len(groups)} grup bulundu")
            return groups
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait: {e.seconds} saniye bekleniyor")
            await asyncio.sleep(e.seconds)
            return await self.search_groups_by_keyword(keyword, limit)
        except Exception as e:
            self.logger.error(f"Grup arama hatası: {str(e)}")
            return []
    
    async def find_active_groups(self, min_members: int = 100, max_results: int = 100) -> List[GroupInfo]:
        """En aktif grupları bul"""
        try:
            all_groups = []
            
            # Farklı dillerde anahtar kelimelerle ara
            for lang, keywords in self.search_keywords.items():
                for keyword in keywords[:3]:  # Her dilde 3 anahtar kelime
                    groups = await self.search_groups_by_keyword(keyword, 20)
                    all_groups.extend(groups)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(2, 5))
            
            # Üye sayısına göre filtrele
            active_groups = [
                group for group in all_groups 
                if group.members_count >= min_members
            ]
            
            # Benzersiz grupları al (ID'ye göre)
            unique_groups = {}
            for group in active_groups:
                if group.id not in unique_groups:
                    unique_groups[group.id] = group
            
            # Üye sayısına göre sırala
            sorted_groups = sorted(
                unique_groups.values(), 
                key=lambda x: x.members_count, 
                reverse=True
            )
            
            return sorted_groups[:max_results]
            
        except Exception as e:
            self.logger.error(f"Aktif grup bulma hatası: {str(e)}")
            return []
    
    async def search_by_language(self, language: str, limit: int = 50) -> List[GroupInfo]:
        """Dile göre grup ara"""
        if language not in self.search_keywords:
            self.logger.warning(f"Desteklenmeyen dil: {language}")
            return []
        
        all_groups = []
        keywords = self.search_keywords[language]
        
        for keyword in keywords:
            groups = await self.search_groups_by_keyword(keyword, limit // len(keywords))
            all_groups.extend(groups)
            
            # Rate limiting
            await asyncio.sleep(random.uniform(2, 4))
        
        return all_groups[:limit]
    
    def export_to_csv(self, groups: List[GroupInfo], filename: str = None):
        """Grupları CSV'ye aktar"""
        if filename is None:
            filename = f"groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Title', 'Username', 'Members', 'Description', 
                           'Verified', 'Scam', 'Restricted', 'Date'])
            
            for group in groups:
                writer.writerow([
                    group.id,
                    group.title,
                    group.username,
                    group.members_count,
                    group.description,
                    group.is_verified,
                    group.is_scam,
                    group.is_restricted,
                    group.date.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        self.logger.info(f"{len(groups)} grup {filename} dosyasına aktarıldı")
        return filename
    
    def export_to_json(self, groups: List[GroupInfo], filename: str = None):
        """Grupları JSON'a aktar"""
        if filename is None:
            filename = f"groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # datetime objelerini string'e çevir
        groups_data = []
        for group in groups:
            group_dict = asdict(group)
            group_dict['date'] = group.date.strftime('%Y-%m-%d %H:%M:%S')
            groups_data.append(group_dict)
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(groups_data, file, ensure_ascii=False, indent=2)
        
        self.logger.info(f"{len(groups)} grup {filename} dosyasına aktarıldı")
        return filename
    
    def get_statistics(self) -> Dict:
        """İstatistikleri al"""
        if not self.found_groups:
            return {}
        
        total_groups = len(self.found_groups)
        total_members = sum(group.members_count for group in self.found_groups)
        avg_members = total_members / total_groups if total_groups > 0 else 0
        
        verified_count = sum(1 for group in self.found_groups if group.is_verified)
        scam_count = sum(1 for group in self.found_groups if group.is_scam)
        restricted_count = sum(1 for group in self.found_groups if group.is_restricted)
        
        return {
            'total_groups': total_groups,
            'total_members': total_members,
            'average_members': round(avg_members, 2),
            'verified_groups': verified_count,
            'scam_groups': scam_count,
            'restricted_groups': restricted_count,
            'search_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Kullanım örneği
async def example_usage():
    """Kullanım örneği"""
    from telethon import TelegramClient
    
    # Client'ınızı oluşturun
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()
    
    # Grup bulucuyu başlat
    finder = GroupFinder(client)
    
    # Anahtar kelime ile ara
    groups = await finder.search_groups_by_keyword("yazılım", 50)
    print(f"'yazılım' ile {len(groups)} grup bulundu")
    
    # Aktif grupları bul
    active_groups = await finder.find_active_groups(min_members=1000, max_results=100)
    print(f"{len(active_groups)} aktif grup bulundu")
    
    # Türkçe gruplar
    tr_groups = await finder.search_by_language('tr', 30)
    print(f"{len(tr_groups)} Türkçe grup bulundu")
    
    # İstatistikler
    stats = finder.get_statistics()
    print("İstatistikler:", stats)
    
    # Export
    finder.export_to_csv(active_groups, "active_groups.csv")
    finder.export_to_json(active_groups, "active_groups.json")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(example_usage())
