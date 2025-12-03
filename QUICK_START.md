# 🚀 Hızlı Başlangıç - Web Panel Deployment

## 1️⃣ Render.com ile Deploy (5 Dakika)

### Adım 1: GitHub'a Push
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/KULLANICI_ADINIZ/telegram-panel.git
git push -u origin main
```

### Adım 2: Render'a Deploy
1. [render.com](https://render.com) → Sign Up (GitHub ile giriş yapın)
2. Dashboard → "New +" → "Web Service"
3. GitHub repo'nuzu seçin
4. Ayarlar:
   - **Name:** `telegram-panel`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r web_panel/requirements.txt`
   - **Start Command:** `gunicorn --chdir web_panel app:app`
   - **Instance Type:** `Free`

5. "Advanced" → Environment Variables ekle:
   ```
   SECRET_KEY = rastgele-uzun-string-123456
   JWT_SECRET_KEY = baska-rastgele-string-789012
   PYTHON_VERSION = 3.11.0
   ```

6. "Create Web Service" → Bekleyin (3-5 dakika)

### Adım 3: Giriş Yapın
- URL: `https://telegram-panel.onrender.com` (sizin URL'iniz farklı olacak)
- Kullanıcı: `admin`
- Şifre: `admin123`

✅ **TAMAMLANDI!** Panel artık online.

---

## 2️⃣ Railway.app ile Deploy (Alternatif)

```bash
# Railway CLI yükle
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up

# Environment variables ekle
railway variables set SECRET_KEY=your-secret-key
railway variables set JWT_SECRET_KEY=your-jwt-secret
```

---

## 3️⃣ Lokal Test

```bash
# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
cd web_panel
pip install -r requirements.txt

# Çalıştır
python app.py
```

Tarayıcıda: `http://localhost:5001`

---

## ⚠️ Önemli Notlar

1. **İlk girişten sonra admin şifresini değiştirin!**
2. Ücretsiz Render planı 15 dakika inaktiviteden sonra uyur (ilk istek 30 saniye sürebilir)
3. Production'da mutlaka güçlü SECRET_KEY kullanın

---

## 🆘 Sorun mu var?

### Build hatası alıyorsanız:
```bash
pip install -r web_panel/requirements.txt
```

### Port hatası alıyorsanız:
Render otomatik PORT sağlar, kod zaten hazır.

### Database hatası alıyorsanız:
SQLite otomatik oluşturulur, sorun yok.

---

## 📱 Sonraki Adımlar

- [ ] Admin şifresini değiştir
- [ ] Telegram API bilgilerini ekle (.env)
- [ ] Custom domain bağla (Render'da ücretsiz SSL ile)
- [ ] Monitoring ekle

Başarılar! 🎉
