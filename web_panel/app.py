#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TELEGRAM ÜYE ÇEKME SİSTEMİ - PREMIUM WEB PANELİ
Kurumsal seviyede web tabanlı yönetim paneli

Özellikler:
- Modern responsive tasarım
- Kullanıcı yönetimi ve kimlik doğrulama
- Gerçek zamanlı dashboard
- Premium abonelik sistemi
- API yönetimi
- Güvenlik katmanları
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import json
import secrets
import asyncio
import random
import time
from functools import wraps
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

# Telegram entegrasyonu için parent directory'yi path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

TELEGRAM_AVAILABLE = False
telegram_client = None
smart_inviter = None
bulk_transfer = None

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError
    from telethon.tl.functions.channels import InviteToChannelRequest
    
    # Parent directory'deki modülleri import et
    import sys
    from pathlib import Path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from smart_inviter import SmartInviter
    from bulk_transfer_system import BulkTransferSystem
    
    TELEGRAM_AVAILABLE = True
    print("✅ Telegram modülleri başarıyla yüklendi!")
except ImportError as e:
    print(f"⚠️ Telegram modülleri yüklenemedi: {e}")
    print("Panel çalışacak ama Telegram özellikleri devre dışı olacak.")

# Flask uygulaması oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
# Render için /tmp klasörünü kullan (yazılabilir)
db_path = os.getenv('DATABASE_URL', 'sqlite:////tmp/premium_panel.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    """500 hatası için detaylı bilgi"""
    import traceback
    error_text = traceback.format_exc()
    return f'''
    <html>
    <head><title>Error 500</title></head>
    <body style="font-family: monospace; padding: 20px;">
        <h1>Internal Server Error</h1>
        <pre>{error_text}</pre>
        <hr>
        <p><a href="/">Ana Sayfa</a> | <a href="/health">Health Check</a></p>
    </body>
    </html>
    ''', 500

@app.errorhandler(404)
def not_found(error):
    """404 hatası"""
    return '''
    <html>
    <head><title>404 Not Found</title></head>
    <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1>404 - Sayfa Bulunamadı</h1>
        <p><a href="/">Ana Sayfa</a></p>
    </body>
    </html>
    ''', 404
jwt = JWTManager(app)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Modeller
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Formlar
class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])

class RegisterForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('E-posta', validators=[DataRequired(), Length(min=6, max=120)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifre Tekrar', validators=[DataRequired(), Length(min=6)])

# Route'lar
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('premium_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            session['jwt_token'] = access_token
            session['refresh_token'] = refresh_token
            
            next_page = request.args.get('next')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Giriş başarılı!',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'redirect_url': next_page or url_for('premium_dashboard')
                }), 200
            
            flash('Giriş başarılı!', 'success')
            return redirect(next_page or url_for('premium_dashboard'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Geçersiz kullanıcı adı veya şifre.'}), 401
            flash('Geçersiz kullanıcı adı veya şifre.', 'error')
    
    return render_template('telegram_login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('premium_dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return render_template('register.html', form=form)
        
        new_user = User(username=form.username.data, email=form.email.data, subscription_type='free')
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/legal-warning')
def legal_warning():
    return render_template('legal_warning.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('jwt_token', None)
    session.pop('refresh_token', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def home():
    """Ana sayfa - test için basit response"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('premium_dashboard'))
        else:
            return redirect(url_for('login'))
    except:
        # Database hatası varsa basit sayfa göster
        return '''
        <html>
        <head><title>Telegram Panel</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1>🚀 Telegram Panel</h1>
            <p>Panel başlatılıyor...</p>
            <p><a href="/login">Login</a> | <a href="/health">Health Check</a></p>
        </body>
        </html>
        '''

@app.route('/premium')
@login_required
def premium_dashboard():
    # TODO: Gerçek istatistikleri veritabanından çek
    stats = {
        'total_members': 0,
        'successful_transfers': 0,
        'pending_transfers': 0,
        'failed_transfers': 0
    }
    return render_template('telegram_dashboard.html', title="Ana Sayfa", stats=stats)

@app.route('/premium/member-transfer')
@login_required
def premium_member_transfer():
    return render_template('telegram_transfer.html', title="Üye Aktarımı")

@app.route('/premium/reports')
@login_required
def premium_reports():
    return render_template('telegram_reports.html', title="Raporlar")

@app.route('/premium/settings')
@login_required
def premium_settings():
    return render_template('telegram_settings.html', title="Ayarlar")

@app.route('/premium/promo')
@login_required
def premium_promo():
    return render_template('telegram_promo.html', title="Reklam Mesajı Gönder")

@app.route('/premium/members')
@login_required
def premium_members():
    return render_template('telegram_members.html', title="Üye Listesi")



# API Route'ları
@app.route('/api/v1/get_groups', methods=['GET'])
@login_required
def get_groups_api():
    """Kullanıcının gruplarını getir"""
    if not TELEGRAM_AVAILABLE:
        return jsonify({'error': 'Telegram modülleri yüklü değil'}), 500
    
    # TODO: Telegram client ile grupları çek
    return jsonify({
        'success': True,
        'groups': []
    })

@app.route('/api/v1/get_members', methods=['POST'])
@login_required
def get_members_api():
    """Belirtilen gruptan üyeleri çek"""
    if not TELEGRAM_AVAILABLE:
        return jsonify({'error': 'Telegram modülleri yüklü değil'}), 500
    
    data = request.get_json()
    group_link = data.get('group_link')
    
    if not group_link:
        return jsonify({'error': 'Grup linki gerekli'}), 400
    
    try:
        # Thread-safe asenkron çalıştırma
        import threading
        result_container = {'members': None, 'error': None}
        
        def run_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                members = loop.run_until_complete(fetch_group_members(group_link))
                result_container['members'] = members
                loop.close()
            except Exception as e:
                result_container['error'] = str(e)
        
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join(timeout=120)  # 2 dakika timeout
        
        if result_container['error']:
            return jsonify({'error': result_container['error']}), 500
        
        return jsonify({
            'success': True,
            'members': result_container['members'],
            'total': len(result_container['members'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/transfer_members', methods=['POST'])
@login_required
def transfer_members_api():
    """Üyeleri hedef gruba aktar"""
    if not TELEGRAM_AVAILABLE:
        return jsonify({'error': 'Telegram modülleri yüklü değil'}), 500
    
    data = request.get_json()
    source_group = data.get('source_group')
    target_group = data.get('target_group')
    max_members = data.get('max_members', 50)
    speed = data.get('speed', 'medium')
    
    if not source_group or not target_group:
        return jsonify({'error': 'Kaynak ve hedef grup gerekli'}), 400
    
    try:
        # Thread-safe asenkron çalıştırma
        import threading
        result_container = {'result': None, 'error': None}
        
        def run_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    start_member_transfer(source_group, target_group, max_members, speed)
                )
                result_container['result'] = result
                loop.close()
            except Exception as e:
                result_container['error'] = str(e)
        
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join(timeout=600)  # 10 dakika timeout
        
        if result_container['error']:
            return jsonify({'error': result_container['error']}), 500
        
        return jsonify({
            'success': True,
            'message': 'Aktarım tamamlandı',
            'result': result_container['result']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/check_telegram', methods=['GET'])
@login_required
def check_telegram_api():
    """Telegram bağlantısını kontrol et"""
    connected = False
    if TELEGRAM_AVAILABLE and telegram_client:
        connected = telegram_client.is_connected()
    
    return jsonify({
        'available': TELEGRAM_AVAILABLE,
        'connected': connected
    })

@app.route('/api/v1/send_promo', methods=['POST'])
@login_required
def send_promo_api():
    """Gruplara reklam mesajı gönder"""
    if not TELEGRAM_AVAILABLE:
        return jsonify({'error': 'Telegram modülleri yüklü değil'}), 500
    
    data = request.get_json()
    message = data.get('message')
    groups = data.get('groups', [])
    min_delay = data.get('min_delay', 45)
    max_delay = data.get('max_delay', 75)
    loop_mode = data.get('loop_mode', False)
    
    if not message or not groups:
        return jsonify({'error': 'Mesaj ve grup listesi gerekli'}), 400
    
    try:
        # Thread-safe asenkron çalıştırma
        import threading
        result_container = {'result': None, 'error': None}
        
        def run_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    send_promo_messages(message, groups, min_delay, max_delay, loop_mode)
                )
                result_container['result'] = result
                loop.close()
            except Exception as e:
                result_container['error'] = str(e)
        
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join(timeout=300)  # 5 dakika timeout
        
        if result_container['error']:
            return jsonify({'error': result_container['error']}), 500
        
        return jsonify({
            'success': True,
            'message': 'Mesaj gönderimi tamamlandı',
            'result': result_container['result'],
            'task_id': f'promo_{int(time.time())}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/stop_promo', methods=['POST'])
@login_required
def stop_promo_api():
    """Reklam mesajı gönderimini durdur"""
    # TODO: Background task'ı durdur
    return jsonify({
        'success': True,
        'message': 'Gönderim durduruldu'
    })

# ============================================
# YENİ ÖZELLİKLER - MODÜLER SERVİSLER
# ============================================

@app.route('/user-lookup')
@login_required
def user_lookup_page():
    """Kullanıcı bilgi sorgulama sayfası"""
    return render_template('telegram_user_lookup.html')

@app.route('/api/v1/user_lookup', methods=['POST'])
@login_required
def user_lookup_api():
    """Kullanıcı bilgi sorgulama API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        query_type = data.get('type', 'phone')  # phone veya username
        
        if not query:
            return jsonify({'error': 'Sorgu boş olamaz'}), 400
        
        if not TELEGRAM_AVAILABLE or not telegram_client:
            return jsonify({'error': 'Telegram bağlantısı yok'}), 503
        
        from services.user_lookup_service import UserLookupService
        service = UserLookupService(telegram_client)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if query_type == 'phone':
            result = loop.run_until_complete(service.lookup_by_phone(query))
        else:
            result = loop.run_until_complete(service.lookup_by_username(query))
        
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fake-account-reporter')
@login_required
def fake_account_page():
    """Sahte hesap raporlama sayfası"""
    return render_template('telegram_fake_reporter.html')

@app.route('/api/v1/report_fake', methods=['POST'])
@login_required
def report_fake_api():
    """Sahte hesap raporlama API"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        reason = data.get('reason', 'spam')
        
        if not username:
            return jsonify({'error': 'Kullanıcı adı boş olamaz'}), 400
        
        if not TELEGRAM_AVAILABLE or not telegram_client:
            return jsonify({'error': 'Telegram bağlantısı yok'}), 503
        
        from services.fake_account_service import FakeAccountService
        service = FakeAccountService(telegram_client)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.report_account(username, reason))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/bulk_report_fake', methods=['POST'])
@login_required
def bulk_report_fake_api():
    """Toplu sahte hesap raporlama API"""
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        reason = data.get('reason', 'spam')
        
        if not usernames:
            return jsonify({'error': 'Kullanıcı listesi boş'}), 400
        
        if not TELEGRAM_AVAILABLE or not telegram_client:
            return jsonify({'error': 'Telegram bağlantısı yok'}), 503
        
        from services.fake_account_service import FakeAccountService
        service = FakeAccountService(telegram_client)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.bulk_report(usernames, reason))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hidden-members')
@login_required
def hidden_members_page():
    """Gizli üye keşif sayfası"""
    return render_template('telegram_hidden_members.html')

@app.route('/api/v1/reveal_hidden', methods=['POST'])
@login_required
def reveal_hidden_api():
    """Gizli üyeleri ortaya çıkar API"""
    try:
        data = request.get_json()
        group_link = data.get('group_link', '').strip()
        
        if not group_link:
            return jsonify({'error': 'Grup linki boş olamaz'}), 400
        
        if not TELEGRAM_AVAILABLE or not telegram_client:
            return jsonify({'error': 'Telegram bağlantısı yok'}), 503
        
        from services.hidden_members_service import HiddenMembersService
        service = HiddenMembersService(telegram_client)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.reveal_members(group_link))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Asenkron yardımcı fonksiyonlar
async def init_telegram_client():
    """Telegram client'ı başlat"""
    global telegram_client, smart_inviter, bulk_transfer
    
    if not TELEGRAM_AVAILABLE:
        return False
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    if not api_id or not api_hash or not phone:
        print("⚠️ Telegram API bilgileri .env dosyasında bulunamadı")
        return False
    
    try:
        telegram_client = TelegramClient(phone, api_id, api_hash)
        await telegram_client.start(phone=phone)
        
        # Smart inviter ve bulk transfer'i başlat
        smart_inviter = SmartInviter(telegram_client)
        bulk_transfer = BulkTransferSystem(smart_inviter)
        
        print("✅ Telegram client başarıyla başlatıldı!")
        return True
    except Exception as e:
        print(f"❌ Telegram client başlatılamadı: {e}")
        return False

async def fetch_group_members(group_link: str):
    """Gruptan üyeleri çek - Her thread için yeni client"""
    # Bu thread için yeni bir Telegram client oluştur
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    if not api_id or not api_hash or not phone:
        raise Exception("Telegram API bilgileri .env dosyasında bulunamadı")
    
    # Yeni client oluştur
    client = TelegramClient(phone, api_id, api_hash)
    
    try:
        # Client'ı başlat
        await client.start(phone=phone)
        
        group = await client.get_entity(group_link)
        members = await client.get_participants(group, limit=None)
        
        member_list = []
        for member in members:
            member_list.append({
                'id': member.id,
                'username': member.username or '',
                'first_name': member.first_name or '',
                'last_name': member.last_name or '',
                'is_bot': getattr(member, 'bot', False)
            })
        
        # Üyeleri dosyaya kaydet
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{group.id}_members.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(member_list, f, ensure_ascii=False, indent=4)
        
        print(f"✅ {len(member_list)} üye {filepath} dosyasına kaydedildi")
        
        # Client'ı kapat
        await client.disconnect()
        
        return member_list
    except Exception as e:
        # Hata durumunda client'ı kapat
        try:
            await client.disconnect()
        except:
            pass
        raise Exception(f"Üyeler çekilirken hata: {str(e)}")

async def start_member_transfer(source_group: str, target_group: str, 
                                max_members: int, speed: str):
    """Üye aktarımını başlat - Her thread için yeni client"""
    # Bu thread için yeni bir Telegram client oluştur
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    if not api_id or not api_hash or not phone:
        raise Exception("Telegram API bilgileri .env dosyasında bulunamadı")
    
    # Yeni client oluştur
    client = TelegramClient(phone, api_id, api_hash)
    
    try:
        # Client'ı başlat
        await client.start(phone=phone)
        
        # Kaynak gruptan üyeleri çek
        members = await fetch_group_members(source_group)
        
        # Hedef grubu al
        target = await client.get_entity(target_group)
        
        # Smart inviter ve bulk transfer oluştur
        inviter = SmartInviter(client)
        transfer = BulkTransferSystem(inviter)
        
        # Aktarımı başlat
        result = await transfer.execute_bulk_transfer(
            members[:max_members], 
            target, 
            auto_mode=True
        )
        
        # Client'ı kapat
        await client.disconnect()
        
        return {
            'total': len(members[:max_members]),
            'success': result.get('success', 0),
            'failed': result.get('failed', 0),
            'message': 'Aktarım tamamlandı'
        }
    except Exception as e:
        # Hata durumunda client'ı kapat
        try:
            await client.disconnect()
        except:
            pass
        raise Exception(f"Aktarım sırasında hata: {str(e)}")

async def send_promo_messages(message: str, groups: list, min_delay: int, 
                              max_delay: int, loop_mode: bool):
    """Gruplara reklam mesajı gönder - Her thread için yeni client"""
    import itertools
    
    # Bu thread için yeni bir Telegram client oluştur
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    if not api_id or not api_hash or not phone:
        raise Exception("Telegram API bilgileri .env dosyasında bulunamadı")
    
    # Yeni client oluştur
    client = TelegramClient(phone, api_id, api_hash)
    
    results = {
        'sent': [],
        'failed': [],
        'total': len(groups)
    }
    
    try:
        # Client'ı başlat
        await client.start(phone=phone)
        print("✅ Mesaj gönderimi için yeni client başlatıldı")
        
        # Döngü moduna göre grup listesi
        group_list = itertools.cycle(groups) if loop_mode else groups
        
        for i, group in enumerate(group_list):
            if loop_mode and i >= len(groups) * 10:  # Maksimum 10 döngü
                break
            
            try:
                await client.send_message(group, message)
                results['sent'].append({
                    'group': group,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ {group} grubuna mesaj gönderildi")
                
                # Rastgele bekleme
                if i < len(groups) - 1 or loop_mode:
                    delay = random.randint(min_delay, max_delay)
                    print(f"⏳ {delay} saniye bekleniyor...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                results['failed'].append({
                    'group': group,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ {group} grubuna mesaj gönderilemedi: {e}")
                
                # Hata durumunda da bekle
                await asyncio.sleep(60)
        
        # Client'ı kapat
        await client.disconnect()
        print("✅ Client bağlantısı kapatıldı")
        
        return results
        
    except Exception as e:
        # Hata durumunda client'ı kapat
        try:
            await client.disconnect()
        except:
            pass
        raise Exception(f"Mesaj gönderimi sırasında hata: {str(e)}")

# ============================================
# HEALTH CHECK & MONITORING
# ============================================

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'telegram_available': TELEGRAM_AVAILABLE,
        'telegram_connected': telegram_client is not None and telegram_client.is_connected() if telegram_client else False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_version': '1.0',
        'status': 'operational',
        'features': {
            'member_transfer': True,
            'promo_messages': True,
            'user_lookup': TELEGRAM_AVAILABLE,
            'fake_reporter': TELEGRAM_AVAILABLE,
            'hidden_members': TELEGRAM_AVAILABLE
        }
    })

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', email='admin@example.com', subscription_type='enterprise')
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin kullanıcısı oluşturuldu (admin/admin123)")
        except Exception as e:
            print(f"⚠️ Database initialization hatası: {e}")
            print("Panel çalışacak ama login gerekebilir")
    
    # Telegram client'ı başlat (opsiyonel)
    if TELEGRAM_AVAILABLE:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(init_telegram_client())
            loop.close()
        except Exception as e:
            print(f"⚠️ Telegram client başlatılamadı: {e}")
            print("Panel çalışacak ama Telegram özellikleri manuel başlatılmalı")
    
    # Production için port ayarı
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"\n{'='*50}")
    print(f"🚀 Telegram Panel Başlatıldı!")
    print(f"{'='*50}")
    print(f"📍 URL: http://localhost:{port}")
    print(f"👤 Kullanıcı: admin")
    print(f"🔑 Şifre: admin123")
    print(f"📦 Telegram Modülleri: {'✅ Yüklü' if TELEGRAM_AVAILABLE else '❌ Yüklü Değil'}")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)