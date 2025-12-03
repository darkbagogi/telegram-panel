# 🚀 Telegram Panel - Deployment Rehberi

Modern, güvenli ve ölçeklenebilir Telegram üye yönetim paneli.

## ✨ Özellikler

- 🎨 Modern ve responsive tasarım
- 🔐 JWT tabanlı güvenli kimlik doğrulama
- 📊 Gerçek zamanlı dashboard
- 👥 Üye aktarım sistemi
- 📈 Detaylı raporlama
- 🛡️ Rate limiting ve güvenlik katmanları
- 💎 Premium abonelik sistemi

## 🚀 Hızlı Deployment

### Render.com (Önerilen - Ücretsiz)

1. **GitHub'a Push**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/telegram-panel.git
git push -u origin main
```

2. **Render'da Deploy**
- [render.com](https://render.com) → Sign Up
- "New +" → "Web Service"
- GitHub repo'nuzu bağlayın
- Ayarlar:
  - **Build Command:** `pip install -r web_panel/requirements.txt`
  - **Start Command:** `gunicorn --chdir web_panel app:app`
  
3. **Environment Variables**
```
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
PYTHON_VERSION=3.11.0
```

4. **Deploy!** 🎉

### Railway.app (Alternatif)

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

## 🔧 Lokal Kurulum

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıklar
cd web_panel
pip install -r requirements.txt

# Çalıştır
python app.py
```

Tarayıcı: `http://localhost:5001`

## 🔑 İlk Giriş

- **Kullanıcı:** `admin`
- **Şifre:** `admin123`

⚠️ **İlk girişten sonra mutlaka şifreyi değiştirin!**

## 📁 Proje Yapısı

```
telegram-panel/
├── web_panel/
│   ├── app.py              # Ana Flask uygulaması
│   ├── wsgi.py             # Production entry point
│   ├── requirements.txt    # Python bağımlılıkları
│   ├── templates/          # HTML şablonları
│   │   ├── login.html
│   │   ├── register.html
│   │   └── premium/
│   └── static/             # CSS, JS, resimler
├── Procfile                # Render/Heroku config
├── render.yaml             # Render config
├── runtime.txt             # Python versiyonu
└── README.md
```

## 🔒 Güvenlik

✅ Yapılması gerekenler:
- [ ] Admin şifresini değiştir
- [ ] SECRET_KEY'leri güçlü random string'lerle değiştir
- [ ] HTTPS kullan (Render otomatik sağlar)
- [ ] Rate limiting aktif (zaten var)
- [ ] CORS ayarlarını kontrol et

## 🌐 Custom Domain

Render'da ücretsiz SSL ile custom domain:
1. Render Dashboard → Settings → Custom Domain
2. Domain'inizi ekleyin
3. DNS kayıtlarını güncelleyin
4. SSL otomatik aktif olur

## 📊 Monitoring

Render otomatik monitoring sağlar:
- CPU/Memory kullanımı
- Request logs
- Error tracking

## 🆘 Sorun Giderme

### Build Hatası
```bash
pip install -r web_panel/requirements.txt
```

### Database Hatası
SQLite otomatik oluşturulur. Sorun devam ederse:
```bash
rm web_panel/instance/premium_panel.db
python web_panel/app.py
```

### Port Hatası
Render otomatik PORT environment variable sağlar.

## 📝 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım için lisans gereklidir.

## ⚖️ Yasal Uyarı

Bu sistem sadece yasal amaçlar için kullanılmalıdır:
- ✅ Kendi gruplarınızı yönetmek
- ✅ İzinli üye aktarımları
- ✅ Topluluk yönetimi

Yasak kullanımlar:
- ❌ Spam
- ❌ Dolandırıcılık
- ❌ Bahis/kumar faaliyetleri
- ❌ İzinsiz veri toplama

## 🤝 Destek

Sorularınız için:
- GitHub Issues
- Email: support@example.com

---

Made with ❤️ for the community
