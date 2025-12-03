# ⚡ Render.com Hızlı Başlangıç

## 🚀 5 Dakikada Deploy

### 1️⃣ GitHub'a Yükle
```bash
./deploy_to_render.sh
```

### 2️⃣ Render.com'da Oluştur
1. https://render.com → Sign Up (GitHub ile)
2. **New +** → **Web Service**
3. Repository seç: `telegram-panel`

### 3️⃣ Ayarları Yapılandır
```
Name: telegram-panel
Environment: Python 3
Build Command: pip install -r web_panel/requirements.txt && pip install -r requirements.txt
Start Command: gunicorn --chdir web_panel --bind 0.0.0.0:$PORT app:app --timeout 120 --workers 2
```

### 4️⃣ Environment Variables
```
TELEGRAM_API_ID=31345694
TELEGRAM_API_HASH=58aa29450214bc5d7c2c8f305cb259c4
TELEGRAM_PHONE=+905527925540
FLASK_ENV=production
```

### 5️⃣ Deploy!
**Create Web Service** → Bekle (5-10 dk) → ✅ Hazır!

## 🌐 Erişim

```
URL: https://telegram-panel.onrender.com
User: admin
Pass: admin123
```

## 📊 Özellikler

✅ Üye Çekme & Aktarım
✅ Reklam Mesajları
✅ Kullanıcı Sorgulama
✅ Sahte Hesap Raporlama
✅ Gizli Üye Keşfi
✅ Otomatik SSL
✅ 7/24 Erişim (ücretli planda)

## 🔧 Sorun Giderme

### Build Hatası
```bash
# Logs kontrol et
Render Dashboard → Logs

# Genellikle çözüm:
pip install -r requirements.txt
```

### Telegram Bağlanamıyor
```bash
# Session dosyası gerekli
# Lokal'de oluştur:
python main.py

# Sonra Render'a yükle (Persistent Disk)
```

## 💰 Maliyet

**Ücretsiz Plan:**
- 750 saat/ay
- 512 MB RAM
- 15 dk inaktivite → uyku

**Starter Plan ($7/ay):**
- 7/24 aktif
- 2 GB RAM
- Daha hızlı

## 📖 Detaylı Rehber

Daha fazla bilgi için: `RENDER_DEPLOYMENT.md`

## ✅ Checklist

- [ ] GitHub'a push edildi
- [ ] Render.com hesabı açıldı
- [ ] Web service oluşturuldu
- [ ] Environment variables eklendi
- [ ] Deploy başarılı
- [ ] Panel açılıyor
- [ ] Admin girişi yapıldı
- [ ] Şifre değiştirildi

## 🎉 Başarılı!

Panel artık canlı: https://telegram-panel.onrender.com

Tüm özellikler web üzerinden kullanılabilir! 🚀
