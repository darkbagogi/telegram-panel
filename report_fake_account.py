#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sahte Hesap Bildirme Aracı
Yasal yollarla Telegram'a sahte hesap bildirimi
"""

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonCopyright,
    InputReportReasonOther
)

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

SESSION_NAME = f"{PHONE}_report"
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════╗
║  🚨 SAHTE HESAP BİLDİRME ARACI 🚨                    ║
║  Yasal Yollarla Telegram'a Bildirme                  ║
╚═══════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.WARNING}⚠️  UYARI: Bu araç sadece YASAL bildirme içindir!{Colors.ENDC}
{Colors.FAIL}❌ Spam yapmak, saldırı düzenlemek YASADIŞ ve SUÇTUR!{Colors.ENDC}
{Colors.GREEN}✅ Sadece gerçek sahte hesapları bildirin.{Colors.ENDC}
"""
    print(banner)

async def report_account(username, reason_type, message):
    """Hesabı Telegram'a bildir"""
    try:
        # Hesabı al
        entity = await client.get_entity(username)
        
        # Bildirme nedenini seç
        reasons = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonFake(),
            '3': InputReportReasonViolence(),
            '4': InputReportReasonPornography(),
            '5': InputReportReasonCopyright(),
            '6': InputReportReasonOther()
        }
        
        reason = reasons.get(reason_type, InputReportReasonFake())
        
        # Telegram'a bildir
        await client(ReportPeerRequest(
            peer=entity,
            reason=reason,
            message=message
        ))
        
        return True
    except Exception as e:
        print(f"{Colors.FAIL}❌ Hata: {e}{Colors.ENDC}")
        return False

async def main():
    print_banner()
    
    # Telegram'a bağlan
    await client.start(phone=PHONE)
    print(f"{Colors.GREEN}✅ Telegram'a bağlandı!{Colors.ENDC}\n")
    
    # Yasal uyarı
    print(f"{Colors.BOLD}{Colors.WARNING}📋 YASAL SORUMLULUK BİLDİRİMİ{Colors.ENDC}")
    print("=" * 60)
    print("Bu aracı kullanarak:")
    print("1. Sadece gerçek sahte hesapları bildireceğinizi")
    print("2. Yanlış/kötü niyetli bildirme yapmayacağınızı")
    print("3. Spam veya saldırı amaçlı kullanmayacağınızı")
    print("4. Tüm yasal sorumluluğu kabul ettiğinizi")
    print("beyan edersiniz.")
    print("=" * 60)
    
    accept = input(f"\n{Colors.BOLD}Kabul ediyor musunuz? (EVET yazın): {Colors.ENDC}").strip()
    
    if accept != "EVET":
        print(f"\n{Colors.WARNING}⚠️  İşlem iptal edildi.{Colors.ENDC}")
        await client.disconnect()
        return
    
    while True:
        print(f"\n{Colors.BOLD}🚨 SAHTE HESAP BİLDİRME{Colors.ENDC}")
        print("=" * 60)
        
        # Sahte hesap bilgisi
        fake_account = input(f"\n{Colors.BOLD}Sahte hesabın kullanıcı adı (@username): {Colors.ENDC}").strip()
        
        if not fake_account:
            print(f"{Colors.FAIL}❌ Kullanıcı adı girmediniz!{Colors.ENDC}")
            continue
        
        # @ işaretini kaldır
        if fake_account.startswith('@'):
            fake_account = fake_account[1:]
        
        # Bildirme nedeni
        print(f"\n{Colors.BOLD}📋 Bildirme Nedeni:{Colors.ENDC}")
        print("1. Spam")
        print("2. Sahte/Taklit Hesap (Fake)")
        print("3. Şiddet")
        print("4. Pornografi")
        print("5. Telif Hakkı İhlali")
        print("6. Diğer")
        
        reason = input(f"\n{Colors.BOLD}Seçiminiz (1-6): {Colors.ENDC}").strip()
        
        if reason not in ['1', '2', '3', '4', '5', '6']:
            print(f"{Colors.FAIL}❌ Geçersiz seçim!{Colors.ENDC}")
            continue
        
        # Açıklama
        print(f"\n{Colors.BOLD}📝 Açıklama:{Colors.ENDC}")
        message = input("Detaylı açıklama girin: ").strip()
        
        if not message:
            message = "Bu hesap sahte/taklit bir hesaptır."
        
        # Onay
        print(f"\n{Colors.BOLD}📊 BİLDİRİM ÖZETİ:{Colors.ENDC}")
        print("=" * 60)
        print(f"Sahte Hesap: @{fake_account}")
        print(f"Neden: {['Spam', 'Sahte/Taklit', 'Şiddet', 'Pornografi', 'Telif', 'Diğer'][int(reason)-1]}")
        print(f"Açıklama: {message}")
        print("=" * 60)
        
        confirm = input(f"\n{Colors.BOLD}Bildirimi göndermek istediğinizden emin misiniz? (e/h): {Colors.ENDC}").lower()
        
        if confirm != 'e':
            print(f"{Colors.WARNING}⚠️  İşlem iptal edildi.{Colors.ENDC}")
            continue
        
        # Bildir
        print(f"\n{Colors.CYAN}📤 Telegram'a bildiriliyor...{Colors.ENDC}")
        
        success = await report_account(fake_account, reason, message)
        
        if success:
            print(f"\n{Colors.GREEN}✅ Başarıyla bildirildi!{Colors.ENDC}")
            print(f"\n{Colors.CYAN}📋 Sonraki Adımlar:{Colors.ENDC}")
            print("1. Telegram 3-7 gün içinde inceleyecek")
            print("2. E-posta ile de bildirebilirsiniz: abuse@telegram.org")
            print("3. Takipçilerinizi bilgilendirin")
            print("4. Kanıt ekran görüntüleri alın")
        else:
            print(f"\n{Colors.FAIL}❌ Bildirme başarısız oldu!{Colors.ENDC}")
        
        # Devam
        another = input(f"\n{Colors.BOLD}Başka bir hesap bildirmek ister misiniz? (e/h): {Colors.ENDC}").lower()
        
        if another != 'e':
            print(f"\n{Colors.CYAN}👋 İşlem tamamlandı!{Colors.ENDC}")
            print(f"\n{Colors.GREEN}💡 Hatırlatma:{Colors.ENDC}")
            print("- Yasal yolları kullandınız ✅")
            print("- Spam yapmadınız ✅")
            print("- Telegram kurallarına uydunuz ✅")
            break
    
    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  İşlem kullanıcı tarafından iptal edildi.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Hata: {e}{Colors.ENDC}")
