# 🚀 Telegram Web Panel

Modern, Telegram tarzında tasarlanmış üye yönetim paneli.

## ✨ Özellikler

### 🎨 Tasarım
- ✅ Telegram'ın orijinal renk paleti (#0088cc)
- ✅ Temiz ve minimal arayüz
- ✅ Responsive tasarım (mobil uyumlu)
- ✅ Sol sidebar navigasyon
- ✅ Modern kartlar ve istatistikler

### 🔧 Fonksiyonlar
- ✅ Kullanıcı girişi ve yetkilendirme
- ✅ Dashboard istatistikleri
- ✅ Üye aktarım sistemi (API hazır)
- ✅ Raporlama sayfası
- ✅ Ayarlar yönetimi
- ⏳ Telegram entegrasyonu (devam ediyor)

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle
```bash
cd web_panel
pip install -r requirements.txt
```

### 2. Çalıştır
```bash
python app.py
```

Panel: http://localhost:5001

### 3. Giriş Yap
- **Kullanıcı:** admin
- **Şifre:** admin123

## 📁 Dosya Yapısı

```
web_panel/
├── app.py                      # Ana Flask uygulaması
├── telegram_service.py         # Telegram işlemleri
├── requirements.txt            # Python bağımlılıkları
├── templates/
│   ├── telegram_base.html      # Ana template
│   ├── telegram_login.html     # Giriş sayfası
│   ├── telegram_dashboard.html # Dashboard
│   ├── telegram_transfer.html  # Üye aktarım
│   ├── telegram_reports.html   # Raporlar
│   └── telegram_settings.html  # Ayarlar
└── instance/
    └── premium_panel.db        # SQLite veritabanı
```

## 🔌 API Endpoints

### Telegram Kontrolü
```
GET /api/v1/check_telegram
```

### Grupları Getir
```
GET /api/v1/get_groups
```

### Üyeleri Çek
```
POST /api/v1/get_members
Body: { "group_link": "@grupadi" }
```

### Üye Aktar
```
POST /api/v1/transfer_members
Body: {
  "source_group": "@kaynak",
  "target_group": "@hedef",
  "max_members": 50
}
```

## 🎯 Kullanım

### 1. Dashboard
- Toplam istatistikleri görüntüle
- Hızlı işlemler menüsü
- Son aktiviteler

### 2. Üye Aktarımı
- Kaynak grup seç
- Hedef grup belirle
- Aktarım ayarlarını yapılandır
- Aktarımı başlat ve izle

### 3. Raporlar
- Aktarım geçmişi
- Başarı oranları
- Detaylı istatistikler

### 4. Ayarlar
- Profil bilgileri
- Şifre değiştirme
- Telegram API ayarları

## 🔒 Güvenlik

- JWT tabanlı kimlik doğrulama
- Rate limiting (Flask-Limiter)
- CSRF koruması (Flask-WTF)
- Şifre hashleme (Werkzeug)
- Session yönetimi

## 🌐 Deployment

### Render.com
```bash
# render.yaml dosyası hazır
# GitHub'a push et ve Render'da bağla
```

### Railway.app
```bash
railway init
railway up
```

### Lokal Test
```bash
python app.py
# http://localhost:5001
```

## 📝 TODO

- [ ] Telegram client entegrasyonunu tamamla
- [ ] WebSocket ile gerçek zamanlı ilerleme
- [ ] Veritabanına aktarım geçmişi kaydet
- [ ] Grafik ve chart'lar ekle
- [ ] Export/Import fonksiyonları
- [ ] Çoklu hesap desteği
- [ ] Zamanlanmış aktarımlar

## 🆘 Sorun Giderme

### Telegram modülleri yüklenmiyor
```bash
pip install telethon python-dotenv
```

### Port zaten kullanımda
```python
# app.py'de port değiştir
app.run(port=5002)
```

### Database hatası
```bash
rm instance/premium_panel.db
python app.py  # Yeniden oluşturulur
```

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Email: support@example.com

---

Made with ❤️ using Telegram's design language
