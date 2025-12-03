#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı Kullanıcı Bilgi Arama
Basit ve hızlı kullanıcı bilgisi çekme
"""

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import os
from dotenv import load_dotenv
import asyncio

# .env dosyasını yükle
load_dotenv()

# API Bilgileri
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE')

async def get_user_info(username_or_id):
    """Kullanıcı bilgilerini al"""
    # Farklı session kullan
    client = TelegramClient(f'{phone}_quick_lookup', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        print("✅ Telegram'a bağlandı!\n")
        
        # Kullanıcıyı al
        user = await client.get_entity(username_or_id)
        
        # Detaylı bilgileri al
        full_user = await client(GetFullUserRequest(user))
        
        # Bilgileri göster
        print("=" * 60)
        print("👤 KULLANICI BİLGİLERİ")
        print("=" * 60)
        
        # Temel bilgiler
        print(f"\n📋 Temel Bilgiler:")
        print(f"  ID: {user.id}")
        print(f"  Kullanıcı Adı: @{user.username}" if user.username else "  Kullanıcı Adı: ❌ Yok")
        print(f"  Ad: {user.first_name}")
        print(f"  Soyad: {user.last_name}" if user.last_name else "  Soyad: -")
        
        # Telefon numarası
        if user.phone:
            print(f"  Telefon: +{user.phone}")
        else:
            print(f"  Telefon: ❌ Gizli veya erişim yok")
        
        # E-posta (API'de yok!)
        print(f"  E-posta: ❌ Telegram API'de e-posta bilgisi bulunmaz!")
        
        # Durum
        print(f"\n🏷️  Durum:")
        if user.bot:
            print(f"  🤖 BOT")
        if hasattr(user, 'premium') and user.premium:
            print(f"  💎 PREMIUM")
        if user.verified:
            print(f"  ✓ DOĞRULANMIŞ")
        if user.scam:
            print(f"  ⚠️ SCAM")
        if user.fake:
            print(f"  ⚠️ FAKE")
        
        # Bio
        if full_user.full_user.about:
            print(f"\n📝 Hakkında:")
            print(f"  {full_user.full_user.about}")
        
        # Ortak gruplar
        if full_user.full_user.common_chats_count > 0:
            print(f"\n👥 Ortak Gruplar: {full_user.full_user.common_chats_count}")
        
        # Profil fotoğrafı
        if full_user.full_user.profile_photo:
            print(f"\n📷 Profil Fotoğrafı: ✅ Var")
        
        print("\n" + "=" * 60)
        
        # Profil linki
        if user.username:
            print(f"\n🔗 Profil Linki: https://t.me/{user.username}")
        
        print()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        await client.disconnect()

# Kullanım
if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════╗
║  🔍 HIZLI KULLANICI BİLGİ ARAMA                      ║
╚═══════════════════════════════════════════════════════╝

⚠️  NOT: E-posta adresi Telegram API'de bulunmaz!
    Sadece telefon numarası (koşullu) alınabilir.
""")
    
    # Kullanıcı adı veya ID iste
    user_input = input("Kullanıcı adı (@username) veya ID girin: ").strip()
    
    if not user_input:
        print("❌ Kullanıcı adı veya ID girmediniz!")
    else:
        # @ işaretini kaldır
        if user_input.startswith('@'):
            user_input = user_input[1:]
        
        # Çalıştır
        asyncio.run(get_user_info(user_input))
