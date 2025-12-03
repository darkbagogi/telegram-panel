#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Kullanıcı Bilgi Arama Aracı
Kullanıcı ID'sinden mevcut bilgileri çeker
"""

import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UserIdInvalidError, FloodWaitError

# .env dosyasını yükle
load_dotenv()

# API Bilgileri
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# Farklı session kullan
SESSION_NAME = f"{PHONE}_user_lookup"
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

class Colors:
    """Terminal renkleri"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Banner göster"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════╗
║  🔍 TELEGRAM KULLANICI BİLGİ ARAMA ARACI 🔍          ║
║  User ID'den Detaylı Bilgi Çekme                     ║
╚═══════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.WARNING}⚠️  ÖNEMLİ UYARI:{Colors.ENDC}
Telegram API güvenlik nedeniyle:
- E-posta adresleri {Colors.FAIL}GÖRÜNMEz{Colors.ENDC}
- Telefon numaraları {Colors.WARNING}SINIRLI{Colors.ENDC} (sadece ortak gruplarda)
- Sadece public bilgiler alınabilir

{Colors.GREEN}✅ Alabileceğiniz Bilgiler:{Colors.ENDC}
- Kullanıcı adı (@username)
- Ad ve soyad
- Bio (hakkında)
- Profil fotoğrafı
- Premium durumu
- Bot durumu
- Doğrulanmış hesap durumu
- Son görülme (gizli değilse)
- Ortak gruplar
- Telefon numarası (sadece ortak gruplarda ve izin varsa)
"""
    print(banner)

async def get_user_info(user_id):
    """Kullanıcı bilgilerini al"""
    try:
        # Kullanıcıyı al
        user = await client.get_entity(int(user_id))
        
        # Detaylı bilgileri al
        full_user = await client(GetFullUserRequest(user))
        
        return user, full_user
    except UserIdInvalidError:
        print(f"{Colors.FAIL}❌ Geçersiz kullanıcı ID!{Colors.ENDC}")
        return None, None
    except ValueError:
        print(f"{Colors.FAIL}❌ Geçersiz ID formatı! Sadece sayı girin.{Colors.ENDC}")
        return None, None
    except Exception as e:
        print(f"{Colors.FAIL}❌ Hata: {e}{Colors.ENDC}")
        return None, None

def print_user_info(user, full_user):
    """Kullanıcı bilgilerini göster"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}👤 KULLANICI BİLGİLERİ{Colors.ENDC}")
    print("═" * 70)
    
    # Temel bilgiler
    print(f"\n{Colors.BOLD}📋 Temel Bilgiler:{Colors.ENDC}")
    print(f"  ID: {Colors.CYAN}{user.id}{Colors.ENDC}")
    
    if user.username:
        print(f"  Kullanıcı Adı: {Colors.GREEN}@{user.username}{Colors.ENDC}")
        print(f"  Profil Linki: {Colors.BLUE}https://t.me/{user.username}{Colors.ENDC}")
    else:
        print(f"  Kullanıcı Adı: {Colors.WARNING}❌ Yok (Gizli hesap){Colors.ENDC}")
    
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    print(f"  Ad Soyad: {Colors.BOLD}{name}{Colors.ENDC}")
    
    # Telefon numarası
    if user.phone:
        print(f"  Telefon: {Colors.GREEN}+{user.phone}{Colors.ENDC}")
    else:
        print(f"  Telefon: {Colors.WARNING}❌ Gizli veya erişim yok{Colors.ENDC}")
    
    # Durum rozetleri
    print(f"\n{Colors.BOLD}🏷️  Durum:{Colors.ENDC}")
    badges = []
    
    if user.bot:
        badges.append(f"{Colors.WARNING}🤖 BOT{Colors.ENDC}")
    
    if getattr(user, 'premium', False):
        badges.append(f"{Colors.BLUE}💎 PREMIUM{Colors.ENDC}")
    
    if user.verified:
        badges.append(f"{Colors.GREEN}✓ DOĞRULANMIŞ{Colors.ENDC}")
    
    if user.scam:
        badges.append(f"{Colors.FAIL}⚠️ SCAM{Colors.ENDC}")
    
    if user.fake:
        badges.append(f"{Colors.FAIL}⚠️ FAKE{Colors.ENDC}")
    
    if user.deleted:
        badges.append(f"{Colors.FAIL}🗑️ SİLİNMİŞ{Colors.ENDC}")
    
    if badges:
        for badge in badges:
            print(f"  {badge}")
    else:
        print(f"  {Colors.GREEN}✅ Normal kullanıcı{Colors.ENDC}")
    
    # Bio (Hakkında)
    if full_user.full_user.about:
        print(f"\n{Colors.BOLD}📝 Hakkında:{Colors.ENDC}")
        print(f"  {full_user.full_user.about}")
    
    # Ortak gruplar
    if full_user.full_user.common_chats_count > 0:
        print(f"\n{Colors.BOLD}👥 Ortak Gruplar:{Colors.ENDC}")
        print(f"  {Colors.GREEN}{full_user.full_user.common_chats_count} ortak grup{Colors.ENDC}")
    
    # Profil fotoğrafı
    if full_user.full_user.profile_photo:
        print(f"\n{Colors.BOLD}📷 Profil Fotoğrafı:{Colors.ENDC}")
        print(f"  {Colors.GREEN}✅ Var{Colors.ENDC}")
    
    # Ek bilgiler
    print(f"\n{Colors.BOLD}ℹ️  Ek Bilgiler:{Colors.ENDC}")
    print(f"  Engellenmiş: {Colors.FAIL if full_user.full_user.blocked else Colors.GREEN}{'Evet' if full_user.full_user.blocked else 'Hayır'}{Colors.ENDC}")
    print(f"  Telefon Aramaları: {Colors.GREEN if full_user.full_user.phone_calls_available else Colors.WARNING}{'Mevcut' if full_user.full_user.phone_calls_available else 'Mevcut Değil'}{Colors.ENDC}")
    print(f"  Video Aramaları: {Colors.GREEN if full_user.full_user.video_calls_available else Colors.WARNING}{'Mevcut' if full_user.full_user.video_calls_available else 'Mevcut Değil'}{Colors.ENDC}")
    
    print("═" * 70)

async def get_common_groups(user_id):
    """Ortak grupları listele"""
    try:
        from telethon.tl.functions.messages import GetCommonChatsRequest
        
        result = await client(GetCommonChatsRequest(
            user_id=int(user_id),
            max_id=0,
            limit=100
        ))
        
        if result.chats:
            print(f"\n{Colors.BOLD}{Colors.HEADER}👥 ORTAK GRUPLAR ({len(result.chats)}){Colors.ENDC}")
            print("═" * 70)
            
            for i, chat in enumerate(result.chats, 1):
                chat_type = "Kanal" if hasattr(chat, 'broadcast') and chat.broadcast else "Grup"
                username = f"@{chat.username}" if hasattr(chat, 'username') and chat.username else "Gizli"
                print(f"{i:2d}. {Colors.BOLD}{chat.title}{Colors.ENDC}")
                print(f"    Tür: {chat_type} | ID: {chat.id} | {username}")
            
            print("═" * 70)
        else:
            print(f"\n{Colors.WARNING}⚠️  Ortak grup bulunamadı{Colors.ENDC}")
    
    except Exception as e:
        print(f"\n{Colors.WARNING}⚠️  Ortak gruplar alınamadı: {e}{Colors.ENDC}")

def save_user_info(user, full_user, user_id):
    """Kullanıcı bilgilerini kaydet"""
    os.makedirs('output', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/user_{user_id}_{timestamp}.json"
    
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'is_bot': user.bot,
        'is_premium': getattr(user, 'premium', False),
        'is_verified': user.verified,
        'is_scam': user.scam,
        'is_fake': user.fake,
        'is_deleted': user.deleted,
        'about': full_user.full_user.about,
        'common_chats_count': full_user.full_user.common_chats_count,
        'blocked': full_user.full_user.blocked,
        'phone_calls_available': full_user.full_user.phone_calls_available,
        'video_calls_available': full_user.full_user.video_calls_available,
        'extracted_at': datetime.now().isoformat()
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{Colors.GREEN}✅ Bilgiler kaydedildi: {filename}{Colors.ENDC}")

async def bulk_lookup():
    """Toplu ID arama"""
    print(f"\n{Colors.BOLD}📋 TOPLU ID ARAMA{Colors.ENDC}")
    print("ID'leri virgül ile ayırarak girin (örn: 123456789, 987654321)")
    
    ids_input = input("ID'ler: ").strip()
    
    if not ids_input:
        print(f"{Colors.FAIL}❌ ID girmediniz!{Colors.ENDC}")
        return
    
    ids = [id.strip() for id in ids_input.split(',')]
    
    print(f"\n{Colors.CYAN}🔍 {len(ids)} kullanıcı aranıyor...{Colors.ENDC}\n")
    
    results = []
    
    for i, user_id in enumerate(ids, 1):
        print(f"{Colors.BOLD}[{i}/{len(ids)}] ID: {user_id}{Colors.ENDC}")
        
        user, full_user = await get_user_info(user_id)
        
        if user and full_user:
            username = f"@{user.username}" if user.username else "Kullanıcı adı yok"
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            phone = f"+{user.phone}" if user.phone else "Gizli"
            
            print(f"  ✅ {username} | {name} | {phone}")
            
            results.append({
                'id': user.id,
                'username': user.username,
                'name': name,
                'phone': user.phone
            })
        else:
            print(f"  ❌ Bulunamadı")
        
        # Rate limit için bekle
        if i < len(ids):
            await asyncio.sleep(1)
    
    # Sonuçları kaydet
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/bulk_lookup_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Colors.GREEN}✅ {len(results)} kullanıcı bilgisi kaydedildi: {filename}{Colors.ENDC}")

async def main():
    """Ana fonksiyon"""
    print_banner()
    
    # Telegram'a bağlan
    await client.start(phone=PHONE)
    print(f"{Colors.GREEN}✅ Telegram'a bağlandı!{Colors.ENDC}\n")
    
    while True:
        print(f"\n{Colors.BOLD}Seçenekler:{Colors.ENDC}")
        print("1. Tek kullanıcı ara")
        print("2. Toplu arama (birden fazla ID)")
        print("3. Çıkış")
        
        choice = input(f"\n{Colors.BOLD}Seçiminiz (1-3): {Colors.ENDC}").strip()
        
        if choice == '1':
            # Tek kullanıcı
            user_id = input(f"\n{Colors.BOLD}Kullanıcı ID girin: {Colors.ENDC}").strip()
            
            if not user_id:
                print(f"{Colors.FAIL}❌ ID girmediniz!{Colors.ENDC}")
                continue
            
            print(f"\n{Colors.CYAN}🔍 Kullanıcı aranıyor...{Colors.ENDC}")
            
            user, full_user = await get_user_info(user_id)
            
            if user and full_user:
                print_user_info(user, full_user)
                
                # Ortak grupları göster
                show_groups = input(f"\n{Colors.BOLD}Ortak grupları görmek ister misiniz? (e/h): {Colors.ENDC}").lower()
                if show_groups == 'e':
                    await get_common_groups(user_id)
                
                # Kaydet
                save_choice = input(f"\n{Colors.BOLD}Bilgileri kaydetmek ister misiniz? (e/h): {Colors.ENDC}").lower()
                if save_choice == 'e':
                    save_user_info(user, full_user, user_id)
        
        elif choice == '2':
            # Toplu arama
            await bulk_lookup()
        
        elif choice == '3':
            print(f"\n{Colors.CYAN}👋 Hoşçakalın!{Colors.ENDC}")
            break
        
        else:
            print(f"{Colors.FAIL}❌ Geçersiz seçim!{Colors.ENDC}")
    
    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  İşlem kullanıcı tarafından iptal edildi.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Hata: {e}{Colors.ENDC}")
