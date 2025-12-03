#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telentro Profil Ayarları Modülü
Kullanıcı profilini özelleştirme ve yönetme
"""

import asyncio
import random
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import base64

from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import InputPeerSelf, InputFile
from telethon.errors import FloodWaitError, UsernameNotOccupiedError, UsernameInvalidError

@dataclass
class ProfileData:
    """Profil bilgisi"""
    first_name: str
    last_name: str
    bio: str
    username: str
    profile_photo_path: Optional[str] = None
    is_verified: bool = False
    is_premium: bool = False
    user_id: int = 0
    phone: str = ""

@dataclass
class ProfileUpdateResult:
    """Profil güncelleme sonucu"""
    success: bool
    field: str
    old_value: str
    new_value: str
    timestamp: datetime
    error_message: Optional[str] = None

class ProfileManager:
    """Profil yöneticisi sınıfı"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.update_history = []
        
        # Profil şablonları
        self.first_names = {
            'tr': ['Ahmet', 'Mehmet', 'Mustafa', 'Ali', 'Hüseyin', 'Hasan', 'İbrahim', 'Ömer', 
                   'Murat', 'Emrah', 'Fatih', 'Yusuf', 'Abdullah', 'Berk', 'Can', 'Barış'],
            'en': ['John', 'Michael', 'David', 'James', 'Robert', 'William', 'Richard', 'Charles',
                   'Joseph', 'Thomas', 'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Mark'],
            'ru': ['Александр', 'Сергей', 'Дмитрий', 'Андрей', 'Алексей', 'Михаил', 'Николай',
                   'Денис', 'Владимир', 'Максим', 'Иван', 'Павел', 'Евгений', 'Виктор']
        }
        
        self.last_names = {
            'tr': ['Yılmaz', 'Kaya', 'Demir', 'Şahin', 'Çelik', 'Öztürk', 'Aydın', 'Özkan',
                   'Arslan', 'Doğan', 'Koç', 'Yıldız', 'Kurt', 'Özdemir', 'Torun'],
            'en': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                   'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas'],
            'ru': ['Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Соколов', 'Лебедев', 'Козлов',
                   'Новиков', 'Морозов', 'Петров', 'Волков', 'Соловьёв', 'Васильев']
        }
        
        self.bio_templates = {
            'professional': [
                "🚀 {job} | {company} 💼\n📍 {location}\n📧 {email}\n🔗 {website}",
                "💡 {job} at {company}\n🎯 {specialty}\n📱 {phone}\n🌐 {website}",
                "👨‍💻 {job} | {industry}\n⚡ {skill}\n📍 {location}\n📧 {email}"
            ],
            'casual': [
                "🎮 {hobby} | {interest}\n📍 {location}\n☕ {coffee}\n🎵 {music}",
                "✨ {personality} | {hobby}\n🌟 {quote}\n📍 {location}",
                "🎯 {goal} | {dream}\n💫 {personality}\n🌈 {vibe}"
            ],
            'business': [
                "💼 {company} | {position}\n📈 {achievement}\n🌍 {market}\n📧 {email}",
                "🏢 {company} Founder\n💡 {innovation}\n🎯 {mission}\n📞 {contact}",
                "🚀 {company} CEO\n💰 {revenue}\n🌟 {award}\n📩 {email}"
            ]
        }
    
    async def get_current_profile(self) -> ProfileData:
        """Mevcut profil bilgilerini al"""
        try:
            me = await self.client.get_me()
            
            profile_data = ProfileData(
                first_name=getattr(me, 'first_name', ''),
                last_name=getattr(me, 'last_name', ''),
                bio=getattr(me, 'about', ''),
                username=getattr(me, 'username', ''),
                user_id=me.id,
                phone=getattr(me, 'phone', ''),
                is_verified=getattr(me, 'verified', False),
                is_premium=getattr(me, 'premium', False)
            )
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Profile info retrieval failed: {e}")
            return ProfileData("", "", "", "", user_id=0)
    
    async def update_first_name(self, new_name: str) -> ProfileUpdateResult:
        """İsim güncelle"""
        try:
            current_profile = await self.get_current_profile()
            old_name = current_profile.first_name
            
            result = await self.client(UpdateProfileRequest(
                first_name=new_name
            ))
            
            update_result = ProfileUpdateResult(
                success=True,
                field='first_name',
                old_value=old_name,
                new_value=new_name,
                timestamp=datetime.now()
            )
            
            self.update_history.append(update_result)
            self.logger.info(f"First name updated: {old_name} -> {new_name}")
            
            return update_result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for first name update: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.update_first_name(new_name)
        except Exception as e:
            self.logger.error(f"First name update failed: {e}")
            return ProfileUpdateResult(False, 'first_name', '', new_name, datetime.now(), str(e))
    
    async def update_last_name(self, new_name: str) -> ProfileUpdateResult:
        """Soyisim güncelle"""
        try:
            current_profile = await self.get_current_profile()
            old_name = current_profile.last_name
            
            result = await self.client(UpdateProfileRequest(
                last_name=new_name
            ))
            
            update_result = ProfileUpdateResult(
                success=True,
                field='last_name',
                old_value=old_name,
                new_value=new_name,
                timestamp=datetime.now()
            )
            
            self.update_history.append(update_result)
            self.logger.info(f"Last name updated: {old_name} -> {new_name}")
            
            return update_result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for last name update: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.update_last_name(new_name)
        except Exception as e:
            self.logger.error(f"Last name update failed: {e}")
            return ProfileUpdateResult(False, 'last_name', '', new_name, datetime.now(), str(e))
    
    async def update_bio(self, new_bio: str) -> ProfileUpdateResult:
        """Biyografi güncelle"""
        try:
            current_profile = await self.get_current_profile()
            old_bio = current_profile.bio
            
            result = await self.client(UpdateProfileRequest(
                about=new_bio
            ))
            
            update_result = ProfileUpdateResult(
                success=True,
                field='bio',
                old_value=old_bio,
                new_value=new_bio,
                timestamp=datetime.now()
            )
            
            self.update_history.append(update_result)
            self.logger.info(f"Bio updated: {old_bio[:30]}... -> {new_bio[:30]}...")
            
            return update_result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for bio update: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.update_bio(new_bio)
        except Exception as e:
            self.logger.error(f"Bio update failed: {e}")
            return ProfileUpdateResult(False, 'bio', '', new_bio, datetime.now(), str(e))
    
    async def update_username(self, new_username: str) -> ProfileUpdateResult:
        """Kullanıcı adı güncelle"""
        try:
            current_profile = await self.get_current_profile()
            old_username = current_profile.username
            
            result = await self.client(UpdateUsernameRequest(
                username=new_username
            ))
            
            update_result = ProfileUpdateResult(
                success=True,
                field='username',
                old_value=old_username,
                new_value=new_username,
                timestamp=datetime.now()
            )
            
            self.update_history.append(update_result)
            self.logger.info(f"Username updated: {old_username} -> {new_username}")
            
            return update_result
            
        except UsernameNotOccupiedError:
            error_msg = f"Username {new_username} is not available"
            self.logger.error(error_msg)
            return ProfileUpdateResult(False, 'username', old_username, new_username, datetime.now(), error_msg)
        except UsernameInvalidError:
            error_msg = f"Username {new_username} is invalid"
            self.logger.error(error_msg)
            return ProfileUpdateResult(False, 'username', old_username, new_username, datetime.now(), error_msg)
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for username update: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.update_username(new_username)
        except Exception as e:
            self.logger.error(f"Username update failed: {e}")
            return ProfileUpdateResult(False, 'username', '', new_username, datetime.now(), str(e))
    
    async def update_profile_photo(self, photo_path: str) -> ProfileUpdateResult:
        """Profil fotoğrafı güncelle"""
        try:
            if not Path(photo_path).exists():
                raise FileNotFoundError(f"Photo file not found: {photo_path}")
            
            # Fotoğrafı yükle
            photo_file = await self.client.upload_file(photo_path)
            
            result = await self.client(UploadProfilePhotoRequest(
                file=photo_file
            ))
            
            update_result = ProfileUpdateResult(
                success=True,
                field='profile_photo',
                old_value='',
                new_value=photo_path,
                timestamp=datetime.now()
            )
            
            self.update_history.append(update_result)
            self.logger.info(f"Profile photo updated: {photo_path}")
            
            return update_result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for photo update: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.update_profile_photo(photo_path)
        except Exception as e:
            self.logger.error(f"Profile photo update failed: {e}")
            return ProfileUpdateResult(False, 'profile_photo', '', photo_path, datetime.now(), str(e))
    
    async def delete_profile_photo(self) -> ProfileUpdateResult:
        """Profil fotoğrafını sil"""
        try:
            # Mevcut fotoğrafları al
            photos = await self.client.get_profile_photos('me')
            
            if photos:
                await self.client(DeletePhotosRequest(photos))
                
                update_result = ProfileUpdateResult(
                    success=True,
                    field='profile_photo',
                    old_value='photo_deleted',
                    new_value='',
                    timestamp=datetime.now()
                )
                
                self.update_history.append(update_result)
                self.logger.info("Profile photo deleted")
                
                return update_result
            else:
                return ProfileUpdateResult(False, 'profile_photo', '', '', datetime.now(), "No photos to delete")
                
        except Exception as e:
            self.logger.error(f"Profile photo deletion failed: {e}")
            return ProfileUpdateResult(False, 'profile_photo', '', '', datetime.now(), str(e))
    
    async def randomize_profile(self, language: str = 'tr', style: str = 'professional') -> Dict[str, ProfileUpdateResult]:
        """Profili rastgele güncelle"""
        results = {}
        
        # Rastgele isim seç
        first_name = random.choice(self.first_names.get(language, self.first_names['tr']))
        last_name = random.choice(self.last_names.get(language, self.last_names['tr']))
        
        # İsim güncelle
        results['first_name'] = await self.update_first_name(first_name)
        await asyncio.sleep(random.uniform(2, 5))
        
        results['last_name'] = await self.update_last_name(last_name)
        await asyncio.sleep(random.uniform(2, 5))
        
        # Bio oluştur
        bio = self.generate_random_bio(style)
        results['bio'] = await self.update_bio(bio)
        await asyncio.sleep(random.uniform(2, 5))
        
        # Rastgele username oluştur
        username = self.generate_random_username(first_name, last_name)
        results['username'] = await self.update_username(username)
        
        return results
    
    def generate_random_bio(self, style: str = 'professional') -> str:
        """Rastgele bio oluştur"""
        templates = self.bio_templates.get(style, self.bio_templates['professional'])
        template = random.choice(templates)
        
        placeholders = {
            '{job}': random.choice(['Software Developer', 'Product Manager', 'Data Scientist', 'UX Designer']),
            '{company}': random.choice(['Tech Corp', 'Digital Solutions', 'Innovation Labs', 'Future Systems']),
            '{location}': random.choice(['Istanbul', 'Ankara', 'Izmir', 'Bursa']),
            '{email}': 'contact@example.com',
            '{website}': 'www.example.com',
            '{phone}': '+90 XXX XXX XX XX',
            '{specialty}': random.choice(['AI/ML', 'Web Development', 'Mobile Apps', 'Cloud Computing']),
            '{skill}': random.choice(['Problem Solving', 'Innovation', 'Leadership', 'Creativity']),
            '{hobby}': random.choice(['Gaming', 'Reading', 'Travel', 'Photography']),
            '{interest}': random.choice(['Technology', 'Music', 'Sports', 'Art']),
            '{coffee}': '☕ Coffee Lover',
            '{music}': '🎵 Music Enthusiast',
            '{personality}': random.choice(['Creative', 'Ambitious', 'Positive', 'Adventurous']),
            '{quote}': random.choice(['Dream Big', 'Stay Positive', 'Never Give Up', 'Be Kind']),
            '{goal}': random.choice(['Success', 'Happiness', 'Growth', 'Freedom']),
            '{dream}': random.choice(['Travel the World', 'Build Something Amazing', 'Help Others']),
            '{vibe}': random.choice(['Good Vibes Only', 'Positive Energy', 'Living My Best Life']),
            '{position}': random.choice(['CEO', 'Founder', 'Director', 'Manager']),
            '{industry}': random.choice(['Technology', 'Finance', 'Healthcare', 'Education']),
            '{achievement}': random.choice(['Award Winner', 'Industry Leader', 'Innovation Expert']),
            '{market}': random.choice(['Global', 'European', 'Asian', 'Local']),
            '{contact}': 'contact@company.com',
            '{innovation}': random.choice(['AI Solutions', 'Digital Transformation', 'Smart Systems']),
            '{mission}': random.choice(['Making Impact', 'Creating Value', 'Innovation First']),
            '{revenue}': random.choice(['$1M+', '$5M+', '$10M+', '$50M+']),
            '{award}': random.choice(['Best Innovation', 'Top Leader', 'Excellence Award'])
        }
        
        bio = template
        for placeholder, value in placeholders.items():
            bio = bio.replace(placeholder, value)
        
        return bio
    
    def generate_random_username(self, first_name: str, last_name: str) -> str:
        """Rastgele username oluştur"""
        base = f"{first_name.lower()}_{last_name.lower()}"
        
        # Sayı ekle
        number = random.randint(100, 9999)
        username = f"{base}_{number}"
        
        # Alternatif formatlar
        alternatives = [
            f"{first_name.lower()}{number}",
            f"{last_name.lower()}{number}",
            f"{base}{number}",
            f"{first_name[0].lower()}{last_name.lower()}{number}",
            f"{first_name.lower()}_{number}",
            f"{last_name.lower()}_{number}"
        ]
        
        return random.choice(alternatives)
    
    async def batch_update_profiles(self, profiles: List[Dict], delay_range: Tuple[int, int] = (5, 15)) -> List[ProfileUpdateResult]:
        """Çoklu profil güncelleme"""
        results = []
        
        for profile_config in profiles:
            try:
                # Profil bilgilerini güncelle
                if 'first_name' in profile_config:
                    result = await self.update_first_name(profile_config['first_name'])
                    results.append(result)
                    await asyncio.sleep(random.uniform(*delay_range))
                
                if 'last_name' in profile_config:
                    result = await self.update_last_name(profile_config['last_name'])
                    results.append(result)
                    await asyncio.sleep(random.uniform(*delay_range))
                
                if 'bio' in profile_config:
                    result = await self.update_bio(profile_config['bio'])
                    results.append(result)
                    await asyncio.sleep(random.uniform(*delay_range))
                
                if 'username' in profile_config:
                    result = await self.update_username(profile_config['username'])
                    results.append(result)
                    await asyncio.sleep(random.uniform(*delay_range))
                
                if 'profile_photo' in profile_config:
                    result = await self.update_profile_photo(profile_config['profile_photo'])
                    results.append(result)
                    await asyncio.sleep(random.uniform(*delay_range))
                
            except Exception as e:
                self.logger.error(f"Batch profile update failed: {e}")
                results.append(ProfileUpdateResult(False, 'batch', '', '', datetime.now(), str(e)))
        
        return results
    
    def get_update_history(self) -> List[Dict]:
        """Güncelleme geçmişini al"""
        return [asdict(result) for result in self.update_history]
    
    def export_history(self, filename: str = None):
        """Güncelleme geçmişini dışa aktar"""
        if filename is None:
            filename = f"profile_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        history = self.get_update_history()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Update history exported to: {filename}")
        return filename

# Kullanım örneği
async def example_usage():
    """Kullanım örneği"""
    from telethon import TelegramClient
    
    # Client'ınızı oluşturun
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()
    
    # Profil yöneticisini başlat
    profile_manager = ProfileManager(client)
    
    # Mevcut profili al
    current_profile = await profile_manager.get_current_profile()
    print("Current profile:", current_profile)
    
    # Profil güncelleme
    result = await profile_manager.update_first_name("Ahmet")
    print("Update result:", result)
    
    # Rastgele profil oluştur
    random_results = await profile_manager.randomize_profile('tr', 'professional')
    print("Random profile updates:", random_results)
    
    # Profil fotoğrafı güncelle
    photo_result = await profile_manager.update_profile_photo("profile_photo.jpg")
    print("Photo update result:", photo_result)
    
    # Güncelleme geçmişini al
    history = profile_manager.get_update_history()
    print("Update history:", history)
    
    # Geçmişi dışa aktar
    profile_manager.export_history()
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(example_usage())
