# 🚀 Telegram Panel Deployment Rehberi

## Render.com ile Deployment (Önerilen - Ücretsiz)

### 1. Hazırlık
- [Render.com](https://render.com) hesabı oluşturun
- GitHub'a projenizi push edin

### 2. Render'da Yeni Web Service Oluşturma

1. Render Dashboard'a gidin
2. "New +" butonuna tıklayın
3. "Web Service" seçin
4. GitHub repo'nuzu bağlayın
5. Aşağıdaki ayarları yapın:

**Build & Deploy Ayarları:**
```
Name: telegram-panel
Environment: Python 3
Build Command: pip install -r web_panel/requirements.txt
Start Command: gunicorn --chdir web_panel app:app
```

**Environment Variables:**
```
SECRET_KEY=<random-string-buraya>
JWT_SECRET_KEY=<random-string-buraya>
PYTHON_VERSION=3.11.0
```

3. "Create Web Service" butonuna tıklayın

### 3. Database Kurulumu (Opsiyonel)

Ücretsiz PostgreSQL için:
1. Render Dashboard'da "New +" > "PostgreSQL"
2. Database oluşturun
3. Connection string'i kopyalayın
4. Web service'inizde `DATABASE_URL` environment variable olarak ekleyin

### 4. İlk Giriş

Deployment tamamlandıktan sonra:
- URL: `https://telegram-panel.onrender.com`
- Kullanıcı: `admin`
- Şifre: `admin123`

⚠️ **ÖNEMLİ:** İlk girişten sonra admin şifresini değiştirin!

---

## Alternatif: Railway.app (Ücretsiz)

### 1. Railway Kurulumu

```bash
# Railway CLI yükle
npm i -g @railway/cli

# Login
railway login

# Proje oluştur
railway init

# Deploy
railway up
```

### 2. Environment Variables Ekle

```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set JWT_SECRET_KEY=your-jwt-secret
```

---

## Alternatif: Vercel (Serverless)

Vercel için Flask uygulamasını serverless function'a çevirmemiz gerekir.

### 1. vercel.json Oluştur

```json
{
  "version": 2,
  "builds": [
    {
      "src": "web_panel/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "web_panel/app.py"
    }
  ]
}
```

### 2. Deploy

```bash
npm i -g vercel
vercel
```

---

## Alternatif: PythonAnywhere (Python'a Özel)

1. [PythonAnywhere](https://www.pythonanywhere.com) hesabı oluşturun
2. "Web" sekmesine gidin
3. "Add a new web app" tıklayın
4. Flask seçin
5. Dosyaları upload edin
6. WSGI dosyasını düzenleyin

---

## Lokal Test

Deployment öncesi lokal test:

```bash
cd web_panel
pip install -r requirements.txt
python app.py
```

Tarayıcıda: `http://localhost:5001`

---

## Güvenlik Notları

✅ Production'da mutlaka yapılması gerekenler:
- [ ] Admin şifresini değiştir
- [ ] SECRET_KEY ve JWT_SECRET_KEY'i güçlü random string'lerle değiştir
- [ ] HTTPS kullan (Render otomatik sağlar)
- [ ] Rate limiting aktif (zaten var)
- [ ] Database backup stratejisi belirle

---

## Sorun Giderme

### Build Hatası
```bash
# requirements.txt'i kontrol et
pip install -r web_panel/requirements.txt
```

### Database Hatası
```bash
# Database'i yeniden oluştur
python -c "from web_panel.app import app, db; app.app_context().push(); db.create_all()"
```

### Port Hatası
Render otomatik olarak PORT environment variable sağlar. Kodda:
```python
port = int(os.environ.get('PORT', 5001))
app.run(host='0.0.0.0', port=port)
```
