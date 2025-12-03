#!/bin/bash

# Telegram Üye Çekme Uygulaması Başlatma Scripti

echo "🚀 Telegram Üye Çekme Uygulaması"
echo "================================="

# Virtual environment kontrolü
if [ ! -d "telegram_env" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Lütfen önce kurulum yapın:"
    echo "python3 -m venv telegram_env"
    echo "source telegram_env/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# .env dosyası kontrolü
if [ ! -f ".env" ]; then
    echo "❌ .env dosyası bulunamadı!"
    echo "Lütfen önce API bilgilerinizi .env dosyasına ekleyin."
    echo "Örnek için .env.example dosyasına bakın."
    exit 1
fi

# API bilgileri kontrolü
if grep -q "your_api_id_here" .env; then
    echo "❌ API bilgileri henüz ayarlanmamış!"
    echo "Lütfen .env dosyasındaki API bilgilerini güncelleyin."
    echo "https://my.telegram.org adresinden API bilgilerinizi alabilirsiniz."
    exit 1
fi

echo "✅ Gereksinimler kontrol edildi"
echo "🔄 Uygulama başlatılıyor..."
echo ""

# Virtual environment'ı aktifleştir ve uygulamayı başlat
source telegram_env/bin/activate && python3 main.py