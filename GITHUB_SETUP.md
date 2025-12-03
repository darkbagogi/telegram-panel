# 🔗 GitHub Repository Kurulumu

## 📋 Adım Adım GitHub Kurulumu

### 1️⃣ GitHub'da Yeni Repository Oluştur

1. https://github.com adresine git
2. Sağ üstte **"+"** → **"New repository"** tıkla
3. Repository bilgilerini gir:

```
Repository name: telegram-panel
Description: Telegram Üye Çekme ve Yönetim Paneli
Visibility: Private (önerilen) veya Public
```

4. **"Create repository"** butonuna tıkla

### 2️⃣ Local Repository'yi GitHub'a Bağla

GitHub'da repository oluşturduktan sonra gösterilen komutları kullan:

```bash
# Remote ekle (KULLANICI_ADI yerine kendi kullanıcı adınızı yazın)
git remote add origin https://github.com/KULLANICI_ADI/telegram-panel.git

# Branch'i main olarak ayarla
git branch -M main

# İlk push
git push -u origin main
```

### 3️⃣ Alternatif: SSH ile Bağlantı

SSH key'iniz varsa:

```bash
git remote add origin git@github.com:KULLANICI_ADI/telegram-panel.git
git branch -M main
git push -u origin main
```

## 🔐 GitHub Personal Access Token (Gerekirse)

Eğer HTTPS kullanıyorsanız ve şifre isteniyorsa:

### Token Oluşturma:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token
4. Seçenekler:
   - Note: `telegram-panel`
   - Expiration: 90 days
   - Scopes: `repo` (tümünü seç)
5. Generate token
6. Token'ı kopyala (bir daha gösterilmeyecek!)

### Token Kullanımı:
```bash
# Push yaparken:
Username: GITHUB_KULLANICI_ADI
Password: [TOKEN'I YAPISTIR]
```

## ✅ Doğrulama

Repository başarıyla oluşturuldu mu kontrol et:

```bash
# Remote'u kontrol et
git remote -v

# Çıktı şöyle olmalı:
# origin  https://github.com/KULLANICI_ADI/telegram-panel.git (fetch)
# origin  https://github.com/KULLANICI_ADI/telegram-panel.git (push)

# GitHub'da kontrol et
# https://github.com/KULLANICI_ADI/telegram-panel
```

## 🚀 Render'a Bağlama

GitHub repository hazır olduktan sonra:

### 1. Render.com'a Git
https://render.com → Sign Up/Login

### 2. GitHub ile Bağlan
- "Connect GitHub" butonuna tıkla
- Repository'lere erişim izni ver
- `telegram-panel` repository'sini seç

### 3. Web Service Oluştur
```
Name: telegram-panel
Environment: Python 3
Branch: main
Root Directory: (boş bırak)
Build Command: pip install -r web_panel/requirements.txt && pip install -r requirements.txt
Start Command: gunicorn --chdir web_panel --bind 0.0.0.0:$PORT app:app --timeout 120 --workers 2
```

### 4. Environment Variables Ekle
```
TELEGRAM_API_ID=31345694
TELEGRAM_API_HASH=58aa29450214bc5d7c2c8f305cb259c4
TELEGRAM_PHONE=+905527925540
FLASK_ENV=production
```

### 5. Deploy!
"Create Web Service" → Bekle → ✅ Hazır!

## 📝 Gelecek Güncellemeler

Kod değişikliği yaptığınızda:

```bash
# Değişiklikleri ekle
git add .

# Commit yap
git commit -m "Açıklama mesajı"

# GitHub'a push et
git push origin main

# Render otomatik deploy eder!
```

## 🔧 Sorun Giderme

### "Permission denied" Hatası
```bash
# SSH key ekle veya HTTPS kullan
git remote set-url origin https://github.com/KULLANICI_ADI/telegram-panel.git
```

### "Authentication failed" Hatası
```bash
# Personal Access Token kullan
# Veya SSH key ekle
```

### "Repository not found" Hatası
```bash
# Repository adını kontrol et
# Public/Private ayarını kontrol et
# Erişim izinlerini kontrol et
```

## 📞 Yardım

- GitHub Docs: https://docs.github.com
- Render Docs: https://render.com/docs
- Git Docs: https://git-scm.com/doc

## ✅ Checklist

- [ ] GitHub hesabı var
- [ ] Yeni repository oluşturuldu
- [ ] Local repo GitHub'a bağlandı
- [ ] İlk push yapıldı
- [ ] Render.com hesabı açıldı
- [ ] GitHub Render'a bağlandı
- [ ] Web service oluşturuldu
- [ ] Environment variables eklendi
- [ ] Deploy başarılı
- [ ] Panel çalışıyor

## 🎉 Tamamlandı!

GitHub repository: https://github.com/KULLANICI_ADI/telegram-panel
Render panel: https://telegram-panel.onrender.com

Artık her `git push` ile otomatik deploy olacak! 🚀
