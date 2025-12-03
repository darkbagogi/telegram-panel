# Telegram Üye Çekme Uygulaması

Bu uygulama, Telegram gruplarından üye bilgilerini güvenli ve etik bir şekilde çekmek için tasarlanmıştır.

## ⚠️ ÖNEMLİ UYARILAR

### Etik Kullanım
Bu uygulama **SADECE** aşağıdaki durumlar için kullanılmalıdır:
- ✅ Kendi sahip olduğunuz gruplar
- ✅ İzin aldığınız gruplar  
- ✅ Güvenlik araştırması (etik hacking)
- ✅ Eğitim amaçlı kullanım

### Yasadışı Kullanım YASAKTIR
- ❌ Spam gönderme
- ❌ İzinsiz veri toplama
- ❌ Kişisel verileri kötüye kullanma
- ❌ Taciz veya rahatsız etme

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.8 veya üzeri
- Telegram hesabı
- Telegram API bilgileri

### 2. Paket Kurulumu
```bash
pip install -r requirements.txt
```

### 3. Telegram API Kurulumu
1. [my.telegram.org](https://my.telegram.org) adresine gidin
2. Telefon numaranızla giriş yapın
3. "API development tools" bölümüne gidin
4. Yeni bir uygulama oluşturun
5. `api_id` ve `api_hash` değerlerini alın

### 4. Konfigürasyon
```bash
python config.py
```
Bu komut `.env` dosyası oluşturacaktır. API bilgilerinizi bu dosyaya ekleyin:

```env
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+90xxxxxxxxxx
```

## 📖 Kullanım

### Temel Kullanım
```bash
python main.py
```

### Programlı Kullanım
```python
from telegram_member_extractor import TelegramMemberExtractor

# Extractor oluştur
extractor = TelegramMemberExtractor(api_id, api_hash, phone)

# Bağlan
await extractor.connect()

# Üyeleri çek
members = await extractor.get_group_members('grup_adi', limit=1000)

# Dosyaya kaydet
extractor.save_to_csv('uyeler.csv')
extractor.save_to_json('uyeler.json')

# Bağlantıyı kapat
await extractor.disconnect()
```

## 📊 Özellikler

### Veri Çekme
- Grup üyelerini toplu çekme
- Kullanıcı bilgileri (ID, isim, kullanıcı adı, telefon)
- Son görülme zamanı
- Premium hesap durumu

### Filtreleme
- Kullanıcı adı olanlara göre filtreleme
- Telefon numarası olanlara göre filtreleme
- Premium kullanıcılara göre filtreleme
- İsme göre arama

### Çıktı Formatları
- CSV
- JSON
- Excel (gelecek sürüm)

### Güvenlik
- Rate limiting koruması
- Etik kullanım kontrolleri
- Aktivite loglama
- Hata yönetimi

## 📁 Dosya Yapısı

```
telegram_member_extractor/
├── main.py                 # Ana program
├── telegram_member_extractor.py  # Çekme sınıfı
├── config.py              # Konfigürasyon
├── requirements.txt       # Python paketleri
├── README.md             # Bu dosya
├── .env                  # API bilgileri (oluşturulacak)
├── output/               # Çıktı dosyaları
├── logs/                 # Log dosyaları
└── sessions/             # Telegram oturumları
```

## 🔧 Gelişmiş Kullanım

### Filtreleme Örnekleri
```python
# Sadece kullanıcı adı olanlar
filtered = extractor.filter_members(has_username=True)

# Sadece telefon numarası olanlar
filtered = extractor.filter_members(has_phone=True)

# Premium kullanıcılar
filtered = extractor.filter_members(is_premium=True)

# İsme göre arama
filtered = extractor.filter_members(first_name='Ahmet')
```

### İstatistikler
```python
stats = extractor.get_statistics()
print(f"Toplam üye: {stats['total_members']}")
print(f"Kullanıcı adı olan: {stats['with_username']}")
print(f"Premium kullanıcı: {stats['premium_users']}")
```

## 🛡️ Güvenlik Önlemleri

### Rate Limiting
Telegram API'sinin rate limit kurallarına uyum için:
- Otomatik bekleme süreleri
- Hata yönetimi
- Yeniden deneme mekanizması

### Veri Koruması
- Hassas verilerin güvenli işlenmesi
- Log dosyalarında kişisel bilgi maskeleme
- Oturum dosyalarının güvenli saklanması

### Etik Kontroller
- Kullanım öncesi etik onay
- Aktivite loglama
- Kötüye kullanım önleme

## 🐛 Sorun Giderme

### Yaygın Hatalar

**1. API Hatası**
```
Error: Invalid API ID/Hash
```
Çözüm: API bilgilerinizi kontrol edin.

**2. Telefon Doğrulama**
```
Error: Phone number not registered
```
Çözüm: Telegram'da kayıtlı telefon numarası kullanın.

**3. Rate Limit**
```
FloodWaitError: Too many requests
```
Çözüm: Program otomatik olarak bekleyecektir.

**4. Grup Bulunamadı**
```
Error: No such group
```
Çözüm: Grup kullanıcı adını kontrol edin (@olmadan).

### Log Dosyaları
Detaylı hata bilgileri için `logs/` klasöründeki log dosyalarını kontrol edin.

## 📝 Lisans

Bu proje eğitim ve güvenlik araştırması amaçlı geliştirilmiştir. 
Kullanım sorumluluğu kullanıcıya aittir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit yapın (`git commit -am 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📞 İletişim

Sorularınız için issue açabilir veya güvenlik açıkları için özel mesaj gönderebilirsiniz.

---

**Hatırlatma:** Bu araç sadece etik ve yasal amaçlar için kullanılmalıdır. Kötüye kullanım durumunda sorumluluk kullanıcıya aittir.# telegram-panel
