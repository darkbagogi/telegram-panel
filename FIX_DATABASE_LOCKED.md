# 🔧 "Database is Locked" Hatası Çözümü

## ❌ Hata:
```
❌ Hata: database is locked
```

## 🔍 Neden Oluşur?

Telegram session dosyası (`.session`) aynı anda birden fazla process tarafından kullanılamaz. 

**Senaryolar:**
1. Web paneli çalışırken terminal scripti çalıştırıyorsunuz
2. `main.py` çalışırken `reveal_hidden_members.py` çalıştırıyorsunuz
3. Birden fazla terminal'de aynı scripti çalıştırıyorsunuz

## ✅ Çözümler

### Çözüm 1: Web Panelini Kapat (Önerilen)

```bash
# Web panelini durdur
# Terminal'de Ctrl+C ile durdur veya:
pkill -f "python.*web_panel/app.py"

# Sonra reveal_hidden_members.py'yi çalıştır
python reveal_hidden_members.py
```

### Çözüm 2: Farklı Session Kullan (Otomatik - Düzeltildi)

Script artık otomatik olarak farklı bir session dosyası kullanıyor:
- Web paneli: `+905XXXXXXXXXX.session`
- Reveal script: `+905XXXXXXXXXX_reveal_members.session`

**İlk çalıştırmada:**
1. Telefon numaranızı girin
2. SMS ile gelen kodu girin
3. Session oluşturulacak

**Sonraki çalıştırmalarda:**
- Otomatik giriş yapılacak
- Kod gerekmeyecek

### Çözüm 3: Session Dosyasını Kopyala

```bash
# Mevcut session'ı kopyala
cp +905XXXXXXXXXX.session +905XXXXXXXXXX_backup.session

# Yeni session ile çalıştır
# reveal_hidden_members.py içinde SESSION_NAME'i değiştir
```

### Çözüm 4: Tüm Session'ları Temizle

```bash
# Tüm session dosyalarını sil (dikkatli kullanın!)
rm *.session *.session-journal

# Yeniden giriş yapmanız gerekecek
python reveal_hidden_members.py
```

## 🎯 Hangi Çözümü Kullanmalıyım?

### Senaryo 1: Web Paneli Kullanmıyorum
```bash
# Direkt çalıştır
python reveal_hidden_members.py
```

### Senaryo 2: Web Paneli Çalışıyor
```bash
# Seçenek A: Paneli kapat
pkill -f "python.*web_panel/app.py"
python reveal_hidden_members.py

# Seçenek B: Farklı session kullan (otomatik)
# Script zaten farklı session kullanıyor, direkt çalıştır
python reveal_hidden_members.py
```

### Senaryo 3: Her İkisini de Kullanmak İstiyorum
```bash
# Terminal 1: Web paneli
cd web_panel
python app.py

# Terminal 2: Reveal script (farklı session)
python reveal_hidden_members.py
# İlk çalıştırmada telefon doğrulaması yapın
```

## 🔍 Session Dosyalarını Kontrol Et

```bash
# Mevcut session dosyalarını listele
ls -la *.session

# Çıktı:
# +905XXXXXXXXXX.session              # Web paneli için
# +905XXXXXXXXXX_reveal_members.session  # Reveal script için
```

## ⚠️ Önemli Notlar

### Session Güvenliği
- ✅ Session dosyaları hassas bilgi içerir
- ✅ `.gitignore`'a eklenmiştir
- ❌ Paylaşmayın
- ❌ Public repo'ya yüklemeyin

### Çoklu Session
- ✅ Aynı telefon numarası ile birden fazla session oluşturabilirsiniz
- ✅ Her session farklı bir dosyada saklanır
- ✅ Telegram maksimum 3 aktif session'a izin verir

### Session Temizleme
```bash
# Kullanılmayan session'ları temizle
rm *_backup.session
rm *_old.session
```

## 🆘 Hala Çalışmıyor mu?

### 1. Process'leri Kontrol Et
```bash
# Telegram kullanan process'leri bul
ps aux | grep python | grep telegram

# Hepsini durdur
pkill -f python
```

### 2. Session Dosyasını Sil
```bash
# Sadece reveal script session'ını sil
rm +905XXXXXXXXXX_reveal_members.session*

# Yeniden çalıştır
python reveal_hidden_members.py
```

### 3. Yeni Telefon Numarası Kullan
```bash
# .env dosyasında farklı bir numara kullan
TELEGRAM_PHONE=+905XXXXXXXXXX  # Farklı numara
```

## ✅ Düzeltme Uygulandı

Script artık otomatik olarak farklı session kullanıyor:

```python
# Eski (sorunlu):
client = TelegramClient(PHONE, API_ID, API_HASH)

# Yeni (düzeltilmiş):
SESSION_NAME = f"{PHONE}_reveal_members"
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
```

**Artık web paneli çalışırken de reveal script'i kullanabilirsiniz!** ✅

---

**Son Güncelleme:** 3 Aralık 2025
**Durum:** ✅ Düzeltildi
