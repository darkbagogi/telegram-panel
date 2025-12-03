#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Üye Çekme Uygulaması - Konfigürasyon
"""

import os
from pathlib import Path

class Config:
    """Uygulama konfigürasyonu"""
    
    # Telegram API bilgileri
    # Bu bilgileri https://my.telegram.org adresinden alabilirsiniz
    API_ID = os.getenv('TELEGRAM_API_ID', '')
    API_HASH = os.getenv('TELEGRAM_API_HASH', '')
    PHONE_NUMBER = os.getenv('TELEGRAM_PHONE', '')
    
    # Dosya ayarları
    OUTPUT_DIR = Path('output')
    LOG_DIR = Path('logs')
    SESSION_DIR = Path('sessions')
    
    # Çekme ayarları
    DEFAULT_MEMBER_LIMIT = 1000
    RATE_LIMIT_DELAY = 1  # saniye
    MAX_RETRY_ATTEMPTS = 3
    
    # Güvenlik ayarları
    REQUIRE_ETHICAL_CONFIRMATION = True
    LOG_ALL_ACTIVITIES = True
    ENCRYPT_OUTPUT_FILES = False  # Gelecek özellik
    
    # Çıktı formatları
    SUPPORTED_FORMATS = ['csv', 'json', 'xlsx']
    DEFAULT_FORMAT = 'csv'
    
    @classmethod
    def create_directories(cls):
        """Gerekli dizinleri oluştur"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        cls.SESSION_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Konfigürasyonu doğrula"""
        errors = []
        
        if not cls.API_ID:
            errors.append("TELEGRAM_API_ID gerekli")
        
        if not cls.API_HASH:
            errors.append("TELEGRAM_API_HASH gerekli")
        
        if not cls.PHONE_NUMBER:
            errors.append("TELEGRAM_PHONE gerekli")
        
        return errors

# Örnek .env dosyası içeriği
ENV_TEMPLATE = """
# Telegram API Bilgileri
# https://my.telegram.org adresinden alın
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+90xxxxxxxxxx

# Opsiyonel ayarlar
MEMBER_LIMIT=1000
OUTPUT_FORMAT=csv
"""

if __name__ == "__main__":
    # .env dosyası oluştur
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(ENV_TEMPLATE)
        print(f".env dosyası oluşturuldu: {env_file.absolute()}")
        print("Lütfen API bilgilerinizi .env dosyasına ekleyin.")
    
    # Dizinleri oluştur
    Config.create_directories()
    print("Gerekli dizinler oluşturuldu.")