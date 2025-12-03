import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError, ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.types import Channel

# .env dosyasını yükle
load_dotenv()

# API Bilgileri
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# Telegram Client
client = TelegramClient(PHONE, API_ID, API_HASH)

async def check_group(group_username):
    print(f"'{group_username}' grubu kontrol ediliyor...")
    try:
        await client.connect()
        print("Telegram'a bağlanıldı.")

        # Grubu bul
        target_group = await client.get_entity(group_username)
        print(f"Grup bulundu: '{target_group.title}' (ID: {target_group.id})")

        if isinstance(target_group, Channel) and not target_group.megagroup:
             print("Bu bir kanal. Kanallarda genellikle sadece yöneticiler üye listesini görebilir.")

        print("Üyeler çekilmeye çalışılıyor (hızlı test için ilk 10 üye)...")
        members = []
        async for member in client.iter_participants(target_group, limit=10):
            members.append(member)
        
        member_count = len(members)

        if member_count > 0:
            print(f"✅ Başarılı! {member_count} üye çekilebildi. Üye çekme işleminde bir sorun görünmüyor.")
        else:
            print("❌ Üye çekilemedi. Olası nedenler:")
            print("1. Grubun üye listesi gizli olabilir (sadece yöneticiler görebilir).")
            print("2. Grupta hiç üye olmayabilir.")
            print("3. Hesabınızın bu işlemi yapma yetkisi kısıtlanmış olabilir.")

    except UsernameNotOccupiedError:
        print(f"❌ Hata: '{group_username}' adında bir grup bulunamadı. Lütfen kullanıcı adını kontrol edin.")
    except (ChatAdminRequiredError, ChannelPrivateError):
        print(f"❌ Hata: Bu grubun üyelerini görmek için yönetici olmanız veya gruba üye olmanız gerekiyor. Grup gizli olabilir.")
    except ValueError as e:
        if "Cannot find any entity corresponding to" in str(e):
             print(f"❌ Hata: '{group_username}' adında bir grup bulunamadı. Lütfen kullanıcı adını kontrol edin.")
        else:
            print(f"❌ Beklenmedik bir Değer Hatası oluştu: {e}")
    except Exception as e:
        print(f"❌ Beklenmedik bir hata oluştu: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()
            print("Bağlantı kesildi.")

if __name__ == "__main__":
    group_to_check = "@SosyalMedyaGloball"
    asyncio.run(check_group(group_to_check))