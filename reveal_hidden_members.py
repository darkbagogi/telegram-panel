#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gizli Grup Üyelerini Açığa Çıkarma Aracı
Gizli/private gruplardaki üyeleri görüntüler ve kaydeder
"""

import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Channel, Chat
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError

# .env dosyasını yükle
load_dotenv()

# API Bilgileri
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# Telegram Client - Farklı session dosyası kullan
SESSION_NAME = f"{PHONE}_reveal_members"
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
    UNDERLINE = '\033[4m'

def print_banner():
    """Banner göster"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════╗
║  🔍 GİZLİ GRUP ÜYELERİNİ AÇIĞA ÇIKARMA ARACI 🔍      ║
║  Telegram Private/Gizli Grup Üye Görüntüleyici       ║
╚═══════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

async def get_group_info(group_identifier):
    """Grup bilgilerini al"""
    try:
        entity = await client.get_entity(group_identifier)
        
        print(f"\n{Colors.GREEN}✅ Grup Bulundu!{Colors.ENDC}")
        print(f"{Colors.BOLD}Grup Adı:{Colors.ENDC} {entity.title}")
        print(f"{Colors.BOLD}Grup ID:{Colors.ENDC} {entity.id}")
        
        if hasattr(entity, 'username') and entity.username:
            print(f"{Colors.BOLD}Kullanıcı Adı:{Colors.ENDC} @{entity.username}")
        else:
            print(f"{Colors.WARNING}⚠️  Bu grup gizli/private (kullanıcı adı yok){Colors.ENDC}")
        
        if hasattr(entity, 'participants_count'):
            print(f"{Colors.BOLD}Üye Sayısı:{Colors.ENDC} {entity.participants_count}")
        
        return entity
    except ChannelPrivateError:
        print(f"{Colors.FAIL}❌ Bu gruba erişim yok! Grubun üyesi olmalısınız.{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}❌ Grup bulunamadı: {e}{Colors.ENDC}")
        return None

async def get_members(entity):
    """Grup üyelerini çek"""
    try:
        # Kanal mı kontrol et
        if hasattr(entity, 'broadcast') and entity.broadcast:
            print(f"\n{Colors.WARNING}⚠️  Bu bir KANAL, grup değil!{Colors.ENDC}")
            print(f"{Colors.WARNING}Kanallarda abone listesi Telegram API'de bulunmaz.{Colors.ENDC}")
            print(f"\n{Colors.CYAN}💡 Alternatifler:{Colors.ENDC}")
            print(f"  1. Kanalın tartışma grubunu bulun")
            print(f"  2. Kanal adminlerini görün")
            print(f"  3. Kanal mesajlarını analiz edin")
            
            # Adminleri göster
            try:
                from telethon.tl.types import ChannelParticipantsAdmins
                admins = await client.get_participants(entity, filter=ChannelParticipantsAdmins())
                
                if admins:
                    print(f"\n{Colors.GREEN}👑 KANAL ADMİNLERİ ({len(admins)}){Colors.ENDC}")
                    print("═" * 50)
                    for i, admin in enumerate(admins, 1):
                        username = f"@{admin.username}" if admin.username else "Kullanıcı adı yok"
                        name = f"{admin.first_name or ''} {admin.last_name or ''}".strip()
                        print(f"{i}. {username} | {name}")
                    print("═" * 50)
            except:
                pass
            
            return []
        
        print(f"\n{Colors.CYAN}📥 Üyeler çekiliyor...{Colors.ENDC}")
        
        members = await client.get_participants(entity, limit=None)
        
        print(f"{Colors.GREEN}✅ {len(members)} üye başarıyla çekildi!{Colors.ENDC}\n")
        
        return members
    except ChatAdminRequiredError:
        print(f"{Colors.FAIL}❌ Bu işlem için admin yetkisi gerekiyor!{Colors.ENDC}")
        return []
    except Exception as e:
        print(f"{Colors.FAIL}❌ Üyeler çekilirken hata: {e}{Colors.ENDC}")
        return []

def analyze_members(members):
    """Üyeleri analiz et"""
    stats = {
        'total': len(members),
        'with_username': 0,
        'without_username': 0,
        'bots': 0,
        'premium': 0,
        'verified': 0,
        'deleted': 0,
        'with_phone': 0
    }
    
    member_list = []
    
    for member in members:
        if isinstance(member, User):
            # İstatistikler
            if member.username:
                stats['with_username'] += 1
            else:
                stats['without_username'] += 1
            
            if member.bot:
                stats['bots'] += 1
            
            if hasattr(member, 'premium') and member.premium:
                stats['premium'] += 1
            
            if member.verified:
                stats['verified'] += 1
            
            if member.deleted:
                stats['deleted'] += 1
            
            if member.phone:
                stats['with_phone'] += 1
            
            # Üye bilgisi
            member_info = {
                'id': member.id,
                'username': member.username,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'phone': member.phone,
                'is_bot': member.bot,
                'is_premium': getattr(member, 'premium', False),
                'is_verified': member.verified,
                'is_deleted': member.deleted,
                'access_hash': member.access_hash
            }
            
            member_list.append(member_info)
    
    return stats, member_list

def print_statistics(stats):
    """İstatistikleri göster"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}📊 İSTATİSTİKLER{Colors.ENDC}")
    print("═" * 50)
    print(f"{Colors.BOLD}Toplam Üye:{Colors.ENDC} {stats['total']}")
    print(f"{Colors.GREEN}✅ Kullanıcı Adı Var:{Colors.ENDC} {stats['with_username']} ({stats['with_username']/stats['total']*100:.1f}%)")
    print(f"{Colors.WARNING}⚠️  Kullanıcı Adı Yok:{Colors.ENDC} {stats['without_username']} ({stats['without_username']/stats['total']*100:.1f}%)")
    print(f"{Colors.CYAN}🤖 Bot:{Colors.ENDC} {stats['bots']}")
    print(f"{Colors.BLUE}💎 Premium:{Colors.ENDC} {stats['premium']}")
    print(f"{Colors.GREEN}✓ Doğrulanmış:{Colors.ENDC} {stats['verified']}")
    print(f"{Colors.FAIL}🗑️  Silinmiş Hesap:{Colors.ENDC} {stats['deleted']}")
    print(f"{Colors.CYAN}📱 Telefon Numarası Var:{Colors.ENDC} {stats['with_phone']}")
    print("═" * 50)

def print_members(member_list, show_all=False):
    """Üyeleri göster"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}👥 ÜYE LİSTESİ{Colors.ENDC}")
    print("═" * 80)
    
    limit = len(member_list) if show_all else min(20, len(member_list))
    
    for i, member in enumerate(member_list[:limit], 1):
        username = f"@{member['username']}" if member['username'] else "❌ Kullanıcı adı yok"
        name = f"{member['first_name'] or ''} {member['last_name'] or ''}".strip() or "İsimsiz"
        
        badges = []
        if member['is_bot']:
            badges.append(f"{Colors.WARNING}🤖BOT{Colors.ENDC}")
        if member['is_premium']:
            badges.append(f"{Colors.BLUE}💎PREMIUM{Colors.ENDC}")
        if member['is_verified']:
            badges.append(f"{Colors.GREEN}✓{Colors.ENDC}")
        
        badge_str = " ".join(badges) if badges else ""
        
        print(f"{i:3d}. {Colors.BOLD}{username:25s}{Colors.ENDC} | {name:20s} | ID: {member['id']} {badge_str}")
    
    if not show_all and len(member_list) > 20:
        print(f"\n{Colors.WARNING}... ve {len(member_list) - 20} üye daha{Colors.ENDC}")
    
    print("═" * 80)

def save_to_file(member_list, group_name, group_id):
    """Üyeleri dosyaya kaydet"""
    # Output klasörünü oluştur
    os.makedirs('output', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON formatında kaydet
    json_filename = f"output/{group_id}_{timestamp}_members.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'group_name': group_name,
            'group_id': group_id,
            'extracted_at': datetime.now().isoformat(),
            'total_members': len(member_list),
            'members': member_list
        }, f, ensure_ascii=False, indent=2)
    
    # TXT formatında kaydet (okunabilir)
    txt_filename = f"output/{group_id}_{timestamp}_members.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(f"Grup: {group_name}\n")
        f.write(f"Grup ID: {group_id}\n")
        f.write(f"Çekilme Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Toplam Üye: {len(member_list)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, member in enumerate(member_list, 1):
            f.write(f"{i}. ")
            if member['username']:
                f.write(f"@{member['username']}")
            else:
                f.write("(kullanıcı adı yok)")
            
            f.write(f" | {member['first_name'] or ''} {member['last_name'] or ''}")
            f.write(f" | ID: {member['id']}")
            
            if member['phone']:
                f.write(f" | Tel: {member['phone']}")
            
            if member['is_bot']:
                f.write(" | BOT")
            if member['is_premium']:
                f.write(" | PREMIUM")
            
            f.write("\n")
    
    print(f"\n{Colors.GREEN}✅ Üyeler kaydedildi:{Colors.ENDC}")
    print(f"   📄 JSON: {json_filename}")
    print(f"   📄 TXT:  {txt_filename}")

async def main():
    """Ana fonksiyon"""
    print_banner()
    
    print(f"{Colors.CYAN}🔄 Telegram'a bağlanılıyor...{Colors.ENDC}")
    print(f"{Colors.WARNING}💡 İpucu: Web paneli çalışıyorsa, farklı bir session kullanılıyor.{Colors.ENDC}\n")
    
    # Telegram'a bağlan
    try:
        await client.start(phone=PHONE)
        print(f"{Colors.GREEN}✅ Telegram'a bağlandı!{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Bağlantı hatası: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Web panelini kapatıp tekrar deneyin.{Colors.ENDC}")
        return
    
    while True:
        # Grup bilgisi al
        group_input = input(f"{Colors.BOLD}Grup linki veya kullanıcı adı girin (çıkmak için 'q'): {Colors.ENDC}").strip()
        
        if group_input.lower() == 'q':
            print(f"\n{Colors.CYAN}👋 Hoşçakalın!{Colors.ENDC}")
            break
        
        if not group_input:
            print(f"{Colors.FAIL}❌ Lütfen bir grup girin!{Colors.ENDC}")
            continue
        
        # Grup bilgilerini al
        entity = await get_group_info(group_input)
        
        if not entity:
            continue
        
        # Devam etmek istiyor mu?
        confirm = input(f"\n{Colors.BOLD}Bu gruptan üyeleri çekmek istiyor musunuz? (e/h): {Colors.ENDC}").lower()
        
        if confirm != 'e':
            print(f"{Colors.WARNING}⚠️  İşlem iptal edildi.{Colors.ENDC}")
            continue
        
        # Üyeleri çek
        members = await get_members(entity)
        
        if not members:
            continue
        
        # Analiz et
        stats, member_list = analyze_members(members)
        
        # İstatistikleri göster
        print_statistics(stats)
        
        # Üyeleri göster
        show_all = input(f"\n{Colors.BOLD}Tüm üyeleri göstermek ister misiniz? (e/h, varsayılan: ilk 20): {Colors.ENDC}").lower()
        print_members(member_list, show_all == 'e')
        
        # Dosyaya kaydet
        save = input(f"\n{Colors.BOLD}Üyeleri dosyaya kaydetmek ister misiniz? (e/h): {Colors.ENDC}").lower()
        
        if save == 'e':
            save_to_file(member_list, entity.title, entity.id)
        
        print(f"\n{Colors.GREEN}✅ İşlem tamamlandı!{Colors.ENDC}\n")
        
        # Devam et
        another = input(f"{Colors.BOLD}Başka bir grup için devam etmek ister misiniz? (e/h): {Colors.ENDC}").lower()
        
        if another != 'e':
            print(f"\n{Colors.CYAN}👋 Hoşçakalın!{Colors.ENDC}")
            break
    
    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  İşlem kullanıcı tarafından iptal edildi.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Hata: {e}{Colors.ENDC}")
