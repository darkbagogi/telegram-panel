# 🔍 Gizli Grup Üyelerini Açığa Çıkarma Aracı

Terminal tabanlı, gizli/private Telegram gruplarındaki üyeleri görüntüleme ve kaydetme aracı.

## ✨ Özellikler

### 📊 Detaylı Bilgiler
- ✅ Kullanıcı adı (@username)
- ✅ Ad ve soyad
- ✅ Kullanıcı ID
- ✅ Telefon numarası (varsa)
- ✅ Bot durumu
- ✅ Premium durumu
- ✅ Doğrulanmış hesap durumu
- ✅ Silinmiş hesap tespiti

### 📈 İstatistikler
- Toplam üye sayısı
- Kullanıcı adı olan/olmayan üyeler
- Bot sayısı
- Premium üye sayısı
- Doğrulanmış hesaplar
- Silinmiş hesaplar
- Telefon numarası olan üyeler

### 💾 Kaydetme
- JSON formatında (programatik kullanım için)
- TXT formatında (okunabilir liste)
- Timestamp ile otomatik isimlendirme
- `output/` klasörüne kayıt

## 🚀 Kullanım

### 1. Çalıştırma

```bash
# Virtual environment'ı aktifleştir
source telegram_env/bin/activate

# Scripti çalıştır
python reveal_hidden_members.py
```

### 2. Grup Bilgisi Girme

Script size grup bilgisi soracak:

```
Grup linki veya kullanıcı adı girin: @grupadi
```

**Kabul edilen formatlar:**
- `@grupadi` - Public grup kullanıcı adı
- `https://t.me/grupadi` - Public grup linki
- `https://t.me/joinchat/XXXXX` - Private grup davet linki
- `-1001234567890` - Grup ID

### 3. Üyeleri Görüntüleme

Script otomatik olarak:
1. Grup bilgilerini gösterir
2. Onay ister
3. Üyeleri çeker
4. İstatistikleri gösterir
5. Üye listesini gösterir

### 4. Kaydetme

İsterseniz üyeleri dosyaya kaydedebilirsiniz:
- JSON: Programatik kullanım için
- TXT: İnsan tarafından okunabilir

## 📋 Örnek Çıktı

```
╔═══════════════════════════════════════════════════════╗
║  🔍 GİZLİ GRUP ÜYELERİNİ AÇIĞA ÇIKARMA ARACI 🔍      ║
║  Telegram Private/Gizli Grup Üye Görüntüleyici       ║
╚═══════════════════════════════════════════════════════╝

✅ Telegram'a bağlandı!

Grup linki veya kullanıcı adı girin: @testgrubu

✅ Grup Bulundu!
Grup Adı: Test Grubu
Grup ID: -1001234567890
Kullanıcı Adı: @testgrubu
Üye Sayısı: 150

Bu gruptan üyeleri çekmek istiyor musunuz? (e/h): e

📥 Üyeler çekiliyor...
✅ 150 üye başarıyla çekildi!

📊 İSTATİSTİKLER
══════════════════════════════════════════════════
Toplam Üye: 150
✅ Kullanıcı Adı Var: 120 (80.0%)
⚠️  Kullanıcı Adı Yok: 30 (20.0%)
🤖 Bot: 5
💎 Premium: 15
✓ Doğrulanmış: 3
🗑️  Silinmiş Hesap: 2
📱 Telefon Numarası Var: 45
══════════════════════════════════════════════════

👥 ÜYE LİSTESİ
════════════════════════════════════════════════════════════════════════════════
  1. @kullanici1              | Ahmet Yılmaz         | ID: 123456789 💎PREMIUM
  2. @kullanici2              | Mehmet Demir         | ID: 987654321
  3. ❌ Kullanıcı adı yok     | Ayşe Kaya            | ID: 456789123
...
```

## 🔐 Gizli Gruplar İçin Gereksinimler

### ✅ Yapabilirsiniz:
- Üyesi olduğunuz gizli gruplardaki üyeleri görebilirsiniz
- Davet linki ile katıldığınız gruplardaki üyeleri görebilirsiniz
- Admin olduğunuz gruplardaki tüm bilgileri görebilirsiniz

### ❌ Yapamazsınız:
- Üyesi olmadığınız gizli gruplardaki üyeleri göremezsiniz
- Engellendiğiniz gruplardaki üyeleri göremezsiniz
- Admin yetkisi gerektiren bazı bilgileri göremeyebilirsiniz

## 📁 Çıktı Dosyaları

### JSON Formatı
```json
{
  "group_name": "Test Grubu",
  "group_id": -1001234567890,
  "extracted_at": "2025-12-03T10:30:00",
  "total_members": 150,
  "members": [
    {
      "id": 123456789,
      "username": "kullanici1",
      "first_name": "Ahmet",
      "last_name": "Yılmaz",
      "phone": "+905551234567",
      "is_bot": false,
      "is_premium": true,
      "is_verified": false,
      "is_deleted": false
    }
  ]
}
```

### TXT Formatı
```
Grup: Test Grubu
Grup ID: -1001234567890
Çekilme Tarihi: 2025-12-03 10:30:00
Toplam Üye: 150
================================================================================

1. @kullanici1 | Ahmet Yılmaz | ID: 123456789 | Tel: +905551234567 | PREMIUM
2. @kullanici2 | Mehmet Demir | ID: 987654321
3. (kullanıcı adı yok) | Ayşe Kaya | ID: 456789123
...
```

## 🎯 Kullanım Senaryoları

### 1. Grup Analizi
```bash
python reveal_hidden_members.py
# Grup: @hedefgrup
# Tüm üyeleri göster: e
# Kaydet: e
```

### 2. Rakip Analiz
```bash
# Public rakip grubundaki üyeleri analiz et
python reveal_hidden_members.py
# Grup: @rakipgrup
# İstatistikleri incele
```

### 3. Veri Toplama
```bash
# Birden fazla gruptan veri topla
python reveal_hidden_members.py
# Her grup için tekrarla
# JSON dosyalarını birleştir
```

## ⚠️ Önemli Notlar

### Yasal Uyarı
- ✅ Sadece üyesi olduğunuz gruplarda kullanın
- ✅ Kişisel verileri koruyun (KVKK)
- ❌ İzinsiz veri toplama yapmayın
- ❌ Spam amaçlı kullanmayın

### Teknik Notlar
- Script her seferinde yeni bir session oluşturur
- Büyük gruplarda (10K+ üye) işlem uzun sürebilir
- Telegram rate limit'lerine dikkat edin
- FloodWait hatası alırsanız bekleyin

## 🔧 Sorun Giderme

### "Gruba erişim yok" Hatası
```
❌ Bu gruba erişim yok! Grubun üyesi olmalısınız.
```
**Çözüm:** Önce gruba katılın, sonra tekrar deneyin.

### "Admin yetkisi gerekiyor" Hatası
```
❌ Bu işlem için admin yetkisi gerekiyor!
```
**Çözüm:** Bazı gruplarda sadece adminler üyeleri görebilir.

### "Grup bulunamadı" Hatası
```
❌ Grup bulunamadı
```
**Çözüm:** Grup linkini veya kullanıcı adını kontrol edin.

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Email: support@example.com

---

**Uyarı:** Bu araç sadece eğitim ve araştırma amaçlıdır. Yasal ve etik kurallara uygun kullanın.
