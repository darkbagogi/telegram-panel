# Bu fonksiyonu main.py'deki send_promo_message fonksiyonunun yerine kopyalayın

async def send_promo_message():
    """Gruplara mesaj gönder - Önce mesaj, sonra gruplar"""
    print("\n" + "="*60)
    print("📢 GRUPLARA MESAJ GÖNDERME")
    print("="*60)
    
    # 1. MESAJ GİRİŞİ
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
    
    # Mesajı göster
    print("\n" + "="*60)
    print("📋 GÖNDERİLECEK MESAJ:")
    print("="*60)
    print(promo_message)
    print("="*60)
    
    confirm_msg = input("\n✅ Bu mesajı göndermek istiyor musunuz? (e/h): ").lower()
    if confirm_msg != 'e':
        print("\n❌ İşlem iptal edildi.")
        return
    
    # 2. HEDEF GRUPLARI GİRİŞİ
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
    
    # Grupları göster
    print("\n" + "="*60)
    print(f"🎯 HEDEF GRUPLAR ({len(target_groups)} grup):")
    print("="*60)
    for i, group in enumerate(target_groups, 1):
        print(f"{i}. {group}")
    print("="*60)
    
    # 3. DÖNGÜ MODU
    loop_mode = input("\n🔄 Sürekli döngü modu aktif olsun mu? (e/h): ").lower()
    use_loop = loop_mode == 'e'
    
    if use_loop:
        print(f"\n{Colors.WARNING}⚠️  UYARI: Sürekli döngü modu aktif!{Colors.ENDC}")
        print("Durdurmak için Ctrl+C'ye basın")
    
    # 4. SON ONAY
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
    
    # 5. MESAJ GÖNDERME
    print("\n📢 Mesaj gönderme işlemi başlıyor...")
    print("⚠️  Durdurmak için Ctrl+C'ye basın\n")

    import itertools
    
    if use_loop:
        # Sürekli döngü
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
        # Tek seferlik gönderim
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
