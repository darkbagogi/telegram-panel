#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ana Uygulama Dosyası
Kullanıcı etkileşimi ve menü yönetimi
"""

import os
import asyncio
import random
from dotenv import load_dotenv, set_key
import json
from smart_inviter import SmartInviter
from telethon import TelegramClient
from bulk_transfer_system import BulkTransferSystem

# .env dosyasını yükle
load_dotenv()

# API Bilgileri
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# Telegram Client
client = TelegramClient(PHONE, API_ID, API_HASH)

async def get_group_members():
    """Kullanıcıdan grup bilgisi al ve üyeleri çek"""
    try:
        group_link = input("\n🔗 Üyelerini çekmek istediğiniz grubun linkini veya ID'sini girin: ")
        target_group = await client.get_entity(group_link)
        
        print(f"\n👥 '{target_group.title}' grubundan üyeler çekiliyor...")
        members = await client.get_participants(target_group, limit=None)
        
        output_file = f"output/{target_group.id}_members.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Sadece temel kullanıcı bilgilerini sakla
            member_list = []
            for member in members:
                member_list.append({
                    'id': member.id,
                    'username': member.username,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'is_bot': member.bot
                })
            json.dump(member_list, f, ensure_ascii=False, indent=4)
        
        print(f"\n✅ {len(members)} üye başarıyla '{output_file}' dosyasına kaydedildi.")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")

async def bulk_transfer_wrapper():
    """Toplu aktarım sistemini doğrudan çalıştırır."""
    try:
        file_path = input("\n📂 Üye listesini içeren JSON dosyasının yolunu girin (örn: output/12345_members.json): ")
        target_group_link = input("\n🎯 Üyeleri davet etmek istediğiniz hedef grubun linkini veya ID'sini girin: ")

        with open(file_path, 'r', encoding='utf-8') as f:
            members = json.load(f)

        target_group = await client.get_entity(target_group_link)
        inviter = SmartInviter(client)
        
        # Toplu aktarım sistemini başlat (yeni agresif ayarlar varsayılan olacak)
        transfer_system = BulkTransferSystem(inviter)

        # Aktarımı çalıştır
        await transfer_system.execute_bulk_transfer(members, target_group, auto_mode=True)

    except FileNotFoundError:
        print(f"\n❌ Hata: Dosya bulunamadı.")
    except Exception as e:
        print(f"\n❌ Beklenmedik bir hata oluştu: {e}")

async def filter_members():
    """Kaydedilmiş üye verilerini filtrele"""
    try:
        file_path = input("\n📂 Filtrelemek istediğiniz üye listesinin JSON dosya yolunu girin: ")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        print("\n🔍 Filtreleme Seçenekleri:")
        print("1. Sadece kullanıcı adı olanlar")
        print("2. Bot olmayanlar")
        
        filter_choice = input("Filtre seçiminizi yapın: ")
        
        if filter_choice == '1':
            filtered_members = [m for m in members if m.get('username')]
        elif filter_choice == '2':
            filtered_members = [m for m in members if not m.get('is_bot')]
        else:
            print("\n❌ Geçersiz filtre seçimi.")
            return
            
        output_file = file_path.replace('.json', '_filtered.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_members, f, ensure_ascii=False, indent=4)
            
        print(f"\n✅ {len(filtered_members)} üye başarıyla filtrelendi ve '{output_file}' dosyasına kaydedildi.")

    except FileNotFoundError:
        print(f"\n❌ Hata: '{file_path}' dosyası bulunamadı.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

async def view_statistics():
    """Kaydedilmiş üye verilerinin istatistiklerini göster"""
    try:
        file_path = input("\n📂 İstatistiklerini görmek istediğiniz üye listesinin JSON dosya yolunu girin: ")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        total_members = len(members)
        bot_count = sum(1 for m in members if m.get('is_bot'))
        with_username_count = sum(1 for m in members if m.get('username'))
        
        print("\n📊 Üye İstatistikleri:")
        print(f"- Toplam Üye Sayısı: {total_members}")
        print(f"- Bot Sayısı: {bot_count}")
        print(f"- Kullanıcı Adı Olan Üye Sayısı: {with_username_count}")
        
        if total_members > 0:
            bot_percentage = (bot_count / total_members) * 100
            with_username_percentage = (with_username_count / total_members) * 100
            print(f"- Bot Oranı: {bot_percentage:.2f}%")
            print(f"- Kullanıcı Adı Olanların Oranı: {with_username_percentage:.2f}%")

    except FileNotFoundError:
        print(f"\n❌ Hata: '{file_path}' dosyası bulunamadı.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

async def change_settings():
    """Uygulama ayarlarını değiştir"""
    env_file = ".env"
    print("\n⚙️ Mevcut Ayarlar:")
    # .env dosyasını oku ve göster
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                print(f"- {line.strip()}")
    
    try:
        key_to_change = input("\nDeğiştirmek istediğiniz ayarın adını girin (örn: MEMBER_LIMIT): ").upper()
        new_value = input(f"'{key_to_change}' için yeni değeri girin: ")
        
        # Değişikliği .env dosyasına yaz
        set_key(env_file, key_to_change, new_value)
        
        print(f"\n✅ '{key_to_change}' ayarı başarıyla '{new_value}' olarak güncellendi.")
        print("Değişikliklerin geçerli olması için uygulamayı yeniden başlatmanız gerekebilir.")

    except Exception as e:
        print(f"\n❌ Hata: {e}")


async def send_promo_message():
    """Gruplara mesaj gönder - Önce mesaj, sonra gruplar"""
    print("\n" + "="*60)
    print("📢 GRUPLARA MESAJ GÖNDERME")
    print("="*60)
    
    print("\n📝 Gönderilecek Mesajı Girin:")
    print("(Çok satırlı mesaj için her satırı girin)")
    print("(Bitirmek için boş satırda Enter'a basın)")
    print("-" * 60)
    
    message_lines = []
    print("Mesaj:")
    while True:
        line = input()
        if line == "" and message_lines:
            break
        if line:
            message_lines.append(line)
    
    promo_message = "\n".join(message_lines)
    
    if not promo_message.strip():
        print("\n❌ Mesaj girmediniz. İşlem iptal edildi.")
        return
    
    print("\n" + "="*60)
    print("📋 GÖNDERİLECEK MESAJ:")
    print("="*60)
    print(promo_message)
    print("="*60)
    
    confirm_msg = input("\n✅ Bu mesajı göndermek istiyor musunuz? (e/h): ").lower()
    if confirm_msg != 'e':
        print("\n❌ İşlem iptal edildi.")
        return
    
    print("\n📢 Hedef Grupları Girin:")
    print("(Her satıra bir grup yazın)")
    print("(Bitirmek için boş satırda Enter)")
    print("Örnek: @grup1 veya https://t.me/grup1")
    print("-" * 60)
    
    target_groups = []
    print("Gruplar:")
    while True:
        group = input().strip()
        if group == "" and target_groups:
            break
        if group:
            target_groups.append(group)
    
    if not target_groups:
        print("\n❌ Hiç grup girmediniz. İşlem iptal edildi.")
        return
    
    print("\n" + "="*60)
    print(f"🎯 HEDEF GRUPLAR ({len(target_groups)} grup):")
    print("="*60)
    for i, group in enumerate(target_groups, 1):
        print(f"{i}. {group}")
    print("="*60)
    
    loop_mode = input("\n🔄 Sürekli döngü modu aktif olsun mu? (e/h): ").lower()
    use_loop = loop_mode == 'e'
    
    if use_loop:
        print(f"\n{Colors.WARNING}⚠️  UYARI: Sürekli döngü modu aktif!{Colors.ENDC}")
        print("Durdurmak için Ctrl+C'ye basın")
    
    print("\n" + "="*60)
    print("📊 ÖZET:")
    print(f"- Mesaj uzunluğu: {len(promo_message)} karakter")
    print(f"- Hedef grup sayısı: {len(target_groups)}")
    print(f"- Döngü modu: {'✅ Aktif (Sürekli)' if use_loop else '❌ Pasif (Bir kez)'}")
    print("="*60)
    
    final_confirm = input("\n🚀 Gönderimi başlatmak için 'EVET' yazın: ").strip()
    if final_confirm != "EVET":
        print("\n❌ İşlem iptal edildi.")
        return
    
    print("\n📢 Mesaj gönderme işlemi başlıyor...")
    print("⚠️  Durdurmak için Ctrl+C'ye basın\n")

    import itertools
    
    if use_loop:
        group_cycle = itertools.cycle(target_groups)
        iteration = 0
        
        while True:
            try:
                group = next(group_cycle)
                iteration += 1
                
                print(f"[Döngü {iteration}] -> '{group}' grubuna gönderiliyor...")
                await client.send_message(group, promo_message)
                print(f"✅ Başarıyla gönderildi.")
                
                delay = random.randint(45, 75)
                print(f"⏳ Bekleme: {delay} saniye...\n")
                await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Hata: {e}")
                print("60 saniye beklenip devam edilecek...\n")
                await asyncio.sleep(60)
    else:
        for i, group in enumerate(target_groups, 1):
            try:
                print(f"[{i}/{len(target_groups)}] -> '{group}' grubuna gönderiliyor...")
                await client.send_message(group, promo_message)
                print(f"✅ Başarıyla gönderildi.")
                
                if i < len(target_groups):
                    delay = random.randint(45, 75)
                    print(f"⏳ Bekleme: {delay} saniye...\n")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Hata: {e}")
                print("60 saniye beklenip devam edilecek...\n")
                await asyncio.sleep(60)
        
        print("\n" + "="*60)
        print("✅ TÜM MESAJLAR GÖNDERİLDİ!")
        print(f"📊 Toplam: {len(target_groups)} grup")
        print("="*60)

async def main():
    """Ana uygulama fonksiyonu"""
    print("🚀 Telegram Üye Çekme Uygulaması")
    print("=================================")

    await client.start(PHONE)
    print("✅ Telegram'a başarıyla bağlandı!")

    while True:
        print("\n🔧 Telegram Üye Çekme Aracı")
        print("========================================")
        print("1. 📊 Grup üyelerini çek ve kaydet")
        print("2. 🚀 Toplu Üye Aktarımı (Güvenli)")
        print("3. 🔍 Kayıtlı verileri filtrele (Yakında)")
        print("4. 📈 İstatistikleri görüntüle (Yakında)")
        print("5. ⚙️ Ayarları değiştir (Yakında)")
        print("6. 📢 Gruplara Reklam Mesajı Gönder")
        print("7. 🚪 Çıkış")
        print("========================================")

        choice = input("Seçiminiz: ")

        if choice == '1':
            await get_group_members()
        elif choice == '2':
            await bulk_transfer_wrapper()
        elif choice == '3':
            await filter_members()
        elif choice == '4':
            await view_statistics()
        elif choice == '5':
            await change_settings()
        elif choice == '6':
            await send_promo_message()
        elif choice == '7':
            print("\n👋 Hoşçakalın!")
            break
        else:
            print("\n❌ Geçersiz seçim. Lütfen tekrar deneyin.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())