# 🔒 Telegram API Kısıtlamaları ve Gerçekler

## ❌ Kesinlikle Alınamayan Bilgiler

### 1. E-posta Adresi
**Neden:** Telegram API'de e-posta adresi bilgisi **hiç bulunmaz**.

**Açıklama:**
- Telegram hesabı oluştururken e-posta **opsiyoneldir**
- Birçok kullanıcının e-postası yoktur
- E-posta sadece hesap kurtarma için kullanılır
- API'de bu bilgi **asla** paylaşılmaz

**Alternatifler:**
- ❌ telegram-cli → Alamaz
- ❌ Telethon → Alamaz
- ❌ Pyrogram → Alamaz
- ❌ MTProto → Alamaz
- ❌ Hiçbir yöntem alamaz!

### 2. Kayıt Tarihi
**Neden:** Telegram API'de kayıt tarihi bilgisi **yoktur**.

**Açıklama:**
- Kullanıcının ne zaman kayıt olduğu API'de yok
- Sadece Telegram sunucularında saklanır
- Gizlilik nedeniyle paylaşılmaz

**Tahmin Yöntemleri:**
- User ID'den yaklaşık tahmin (düşük ID = eski kullanıcı)
- Ama kesin tarih **asla** alınamaz

### 3. Şifre
**Neden:** Güvenlik!

**Açıklama:**
- Şifreler hash'lenerek saklanır
- API'de asla bulunmaz
- Telegram bile şifrenizi göremez (2FA)

### 4. Ödeme Bilgileri
**Neden:** PCI-DSS uyumluluğu

**Açıklama:**
- Kredi kartı bilgileri
- Ödeme geçmişi
- Bakiye bilgileri

### 5. Gizli Sohbetler
**Neden:** End-to-end encryption

**Açıklama:**
- Gizli sohbetler cihazda saklanır
- Sunucuda yok
- API'den erişilemez

## ⚠️ Koşullu Alınabilen Bilgiler

### 1. Telefon Numarası

**Ne Zaman Alınır:**
- ✅ Ortak gruplarda
- ✅ Kullanıcı "Herkes görebilir" seçmiş
- ✅ Telefon rehberinizde kayıtlı

**Ne Zaman Alınmaz:**
- ❌ Kullanıcı gizlilik ayarlarında gizlemiş
- ❌ Ortak grubunuz yok
- ❌ Kullanıcı sizi engellemiş

**Kod Örneği:**
```python
user = await client.get_entity(user_id)
if user.phone:
    print(f"Telefon: +{user.phone}")
else:
    print("Telefon: Gizli")
```

### 2. Son Görülme

**Ne Zaman Alınır:**
- ✅ Kullanıcı "Herkes görebilir" seçmiş
- ✅ Karşılıklı son görülme açık

**Ne Zaman Alınmaz:**
- ❌ Kullanıcı gizlemiş
- ❌ Siz de gizlemişseniz (karşılıklılık)

### 3. Profil Fotoğrafı

**Ne Zaman Alınır:**
- ✅ Public profil
- ✅ Ortak gruplarda

**Ne Zaman Alınmaz:**
- ❌ Kullanıcı gizlemiş
- ❌ Sizi engellemiş

## ✅ Her Zaman Alınabilen Bilgiler

### Public Bilgiler

1. **Kullanıcı Adı (@username)**
   ```python
   user.username  # None ise gizli hesap
   ```

2. **Ad ve Soyad**
   ```python
   user.first_name
   user.last_name
   ```

3. **User ID**
   ```python
   user.id  # Benzersiz, değişmez
   ```

4. **Bot Durumu**
   ```python
   user.bot  # True/False
   ```

5. **Premium Durumu**
   ```python
   user.premium  # True/False
   ```

6. **Doğrulanmış Hesap**
   ```python
   user.verified  # True/False (mavi tik)
   ```

7. **Scam/Fake Durumu**
   ```python
   user.scam  # Dolandırıcı işaretli
   user.fake  # Sahte hesap işaretli
   ```

8. **Bio (Hakkında)**
   ```python
   full_user.full_user.about
   ```

9. **Ortak Gruplar**
   ```python
   full_user.full_user.common_chats_count
   ```

## 🔧 Kullanılan Araçlar Karşılaştırması

### telegram-cli (Eski, Önerilmez)
```bash
# Kurulum zor
# Artık geliştirilmiyor
# Aynı API kısıtlamaları
# E-posta alamaz ❌
```

### Telethon (Önerilen) ✅
```python
# Modern, aktif geliştiriliyor
# Python ile kolay kullanım
# Async/await desteği
# Dokümantasyon mükemmel
# E-posta alamaz ❌ (API kısıtlaması)
```

### Pyrogram (Alternatif)
```python
# Modern, hızlı
# Telethon'a benzer
# E-posta alamaz ❌ (API kısıtlaması)
```

### MTProto (Düşük Seviye)
```python
# Çok karmaşık
# Manuel implementasyon
# E-posta alamaz ❌ (API kısıtlaması)
```

## 💡 Gerçekçi Beklentiler

### ✅ Yapabilecekleriniz

1. **Kullanıcı Doğrulama**
   ```python
   # Bot mu, scam mi kontrol et
   if user.bot:
       print("Bu bir bot")
   if user.scam:
       print("Dolandırıcı işaretli!")
   ```

2. **Ortak Grup Analizi**
   ```python
   # Hangi gruplarda birlikte olduğunuzu görün
   common_chats = await client(GetCommonChatsRequest(user_id))
   ```

3. **Public Bilgi Toplama**
   ```python
   # Username, ad, bio, premium durumu
   info = {
       'username': user.username,
       'name': f"{user.first_name} {user.last_name}",
       'premium': user.premium,
       'verified': user.verified
   }
   ```

4. **Telefon Numarası (Koşullu)**
   ```python
   # Sadece ortak gruplarda ve izin varsa
   if user.phone:
       print(f"+{user.phone}")
   ```

### ❌ Yapamayacaklarınız

1. **E-posta Adresi Alma**
   - Hiçbir yöntemle mümkün değil
   - API'de bu bilgi yok

2. **Kayıt Tarihi Öğrenme**
   - Kesin tarih alınamaz
   - Sadece User ID'den tahmin

3. **Gizli Bilgilere Erişim**
   - Şifre
   - Ödeme bilgileri
   - Gizli sohbetler

4. **Gizlilik Ayarlarını Aşma**
   - Kullanıcı gizlemişse göremezsiniz
   - Telegram gizliliği korur

## 🎯 Sonuç

### E-posta ve Kayıt Tarihi İçin:

**Telegram API:** ❌ Alamaz
**telegram-cli:** ❌ Alamaz
**Telethon:** ❌ Alamaz
**Pyrogram:** ❌ Alamaz
**Hiçbir Yöntem:** ❌ Alamaz

**Neden?** Çünkü bu bilgiler Telegram API'de **hiç bulunmaz**!

### Alabileceğiniz Bilgiler:

✅ Kullanıcı adı
✅ Ad soyad
✅ User ID
✅ Bot durumu
✅ Premium durumu
✅ Doğrulanmış hesap
✅ Bio
✅ Ortak gruplar
✅ Profil fotoğrafı
⚠️ Telefon numarası (koşullu)
⚠️ Son görülme (koşullu)

### Önerilen Araç:

**Telethon** (Bizim kullandığımız)
- Modern
- Güvenilir
- İyi dokümante
- Aktif geliştiriliyor

```bash
# Kullanmak için:
python user_info_lookup.py
```

## 📚 Kaynaklar

- [Telegram API Docs](https://core.telegram.org/api)
- [Telethon Docs](https://docs.telethon.dev/)
- [Privacy Policy](https://telegram.org/privacy)

---

**Sonuç:** E-posta ve kayıt tarihi Telegram API'de yoktur ve hiçbir yöntemle alınamaz. Bu bir kısıtlama değil, Telegram'ın gizlilik politikasının bir parçasıdır.
