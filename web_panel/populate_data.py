#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web paneli için örnek veriler oluşturan script
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
import json

# Flask uygulamasını import et
sys.path.append(str(Path(__file__).parent))
from app import app, db, User, Campaign, Statistics, TelegramSession, TelegramGroup, InviteLog, Payment, SubscriptionPlan, TelegramMember

def create_sample_data():
    """Örnek veriler oluştur"""
    with app.app_context():
        print("Örnek veriler oluşturuluyor...")
        
        # Mevcut kullanıcıyı al (admin kullanıcısı olduğunu varsayıyoruz)
        user = User.query.first()
        if not user:
            print("Kullanıcı bulunamadı. Önce giriş yapın.")
            return
        
        print(f"Kullanıcı bulundu: {user.username}")
        
        # 1. İstatistik verileri oluştur (son 30 gün)
        print("İstatistik verileri oluşturuluyor...")
        for i in range(30):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).date()
            
            # Mevcut istatistik var mı kontrol et
            existing_stat = Statistics.query.filter_by(user_id=user.id, date=date).first()
            if not existing_stat:
                invites_sent = random.randint(10, 150)
                success_rate = random.uniform(0.6, 0.9)
                successful = int(invites_sent * success_rate)
                failed = invites_sent - successful
                
                stat = Statistics(
                    user_id=user.id,
                    date=date,
                    invites_sent=invites_sent,
                    invites_successful=successful,
                    invites_failed=failed,
                    revenue=random.uniform(5.0, 50.0)
                )
                db.session.add(stat)
        
        # 2. Telegram oturumları oluştur
        print("Telegram oturumları oluşturuluyor...")
        session_names = [
            "Ana Hesap", "İş Hesabı", "Pazarlama Hesabı", "Yedek Hesap", "Test Hesabı"
        ]
        phone_numbers = [
            "+90555123456", "+90555234567", "+90555345678", "+90555456789", "+90555567890"
        ]
        
        for i, (name, phone) in enumerate(zip(session_names, phone_numbers)):
            existing_session = TelegramSession.query.filter_by(user_id=user.id, session_name=name).first()
            if not existing_session:
                session = TelegramSession(
                    user_id=user.id,
                    session_name=name,
                    phone_number=phone,
                    api_id=str(random.randint(1000000, 9999999)),
                    api_hash=f"{''.join(random.choices('abcdef0123456789', k=32))}",
                    is_active=random.choice([True, True, True, False]),  # %75 aktif
                    last_used=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
                )
                db.session.add(session)
        
        # 3. Telegram grupları oluştur
        print("Telegram grupları oluşturuluyor...")
        group_data = [
            {"title": "Teknoloji Severler", "username": "teknoloji_severler", "type": "supergroup", "members": 15420},
            {"title": "Kripto Para Türkiye", "username": "kripto_turkiye", "type": "supergroup", "members": 8750},
            {"title": "Girişimcilik Topluluğu", "username": "girisimcilik_tr", "type": "supergroup", "members": 12300},
            {"title": "Yazılım Geliştirme", "username": "yazilim_dev", "type": "supergroup", "members": 6890},
            {"title": "E-ticaret Uzmanları", "username": "eticaret_uzman", "type": "supergroup", "members": 4560},
            {"title": "Dijital Pazarlama", "username": "dijital_pazarlama", "type": "supergroup", "members": 9870},
            {"title": "Freelancer Türkiye", "username": "freelancer_tr", "type": "supergroup", "members": 7650},
            {"title": "Startup Ekosistemi", "username": "startup_ekosistem", "type": "supergroup", "members": 5430}
        ]
        
        for group_info in group_data:
            existing_group = TelegramGroup.query.filter_by(user_id=user.id, group_username=group_info["username"]).first()
            if not existing_group:
                group = TelegramGroup(
                    user_id=user.id,
                    group_id=str(random.randint(1000000000, 9999999999)),
                    group_username=group_info["username"],
                    group_title=group_info["title"],
                    group_type=group_info["type"],
                    member_count=group_info["members"],
                    is_admin=random.choice([True, False]),
                    can_invite=random.choice([True, True, False]),  # %66 davet edebilir
                    last_scanned=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))
                )
                db.session.add(group)
        
        # 4. Kampanyalar oluştur
        print("Kampanyalar oluşturuluyor...")
        campaign_names = [
            "Teknoloji Grubu Transfer",
            "Kripto Para Topluluğu Büyütme",
            "Girişimci Ağı Genişletme",
            "Yazılımcı Topluluğu Transfer",
            "E-ticaret Uzmanları Davet",
            "Pazarlama Grubu Büyütme",
            "Freelancer Ağı Transfer",
            "Startup Topluluğu Davet"
        ]
        
        statuses = ["completed", "running", "paused", "pending", "failed"]
        priorities = ["high", "normal", "low"]
        
        for i, name in enumerate(campaign_names):
            existing_campaign = Campaign.query.filter_by(user_id=user.id, name=name).first()
            if not existing_campaign:
                status = random.choice(statuses)
                total_members = random.randint(500, 2000)
                
                if status == "completed":
                    invited = total_members
                    successful = int(invited * random.uniform(0.7, 0.9))
                    progress = 100.0
                elif status == "running":
                    invited = int(total_members * random.uniform(0.3, 0.8))
                    successful = int(invited * random.uniform(0.7, 0.9))
                    progress = (invited / total_members) * 100
                elif status == "paused":
                    invited = int(total_members * random.uniform(0.1, 0.5))
                    successful = int(invited * random.uniform(0.7, 0.9))
                    progress = (invited / total_members) * 100
                else:
                    invited = 0
                    successful = 0
                    progress = 0.0
                
                failed = invited - successful
                
                campaign = Campaign(
                    user_id=user.id,
                    name=name,
                    description=f"{name} için otomatik üye transferi kampanyası",
                    source_group=f"@{group_data[i % len(group_data)]['username']}",
                    target_group=f"@hedef_{group_data[i % len(group_data)]['username']}",
                    status=status,
                    priority=random.choice(priorities),
                    transfer_mode=random.choice(["smart", "bulk", "scheduled"]),
                    daily_limit=random.randint(50, 200),
                    total_members=total_members,
                    invited_members=invited,
                    successful_invites=successful,
                    failed_invites=failed,
                    progress_percentage=progress,
                    filter_settings=json.dumps({
                        "min_last_seen_days": random.randint(1, 30),
                        "exclude_bots": True,
                        "premium_only": random.choice([True, False])
                    }),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
                )
                
                if status in ["running", "completed"]:
                    campaign.started_at = campaign.created_at + timedelta(hours=random.randint(1, 24))
                
                if status == "completed":
                    campaign.completed_at = campaign.started_at + timedelta(hours=random.randint(2, 48))
                
                db.session.add(campaign)
        
        # 5. Kullanıcı istatistiklerini güncelle
        print("Kullanıcı istatistikleri güncelleniyor...")
        total_stats = Statistics.query.filter_by(user_id=user.id).all()
        user.total_invites_sent = sum(stat.invites_sent for stat in total_stats)
        user.successful_invites = sum(stat.invites_successful for stat in total_stats)
        
        # Commit all changes
        db.session.commit()
        print("✅ Örnek veriler başarıyla oluşturuldu!")
        
        # Özet bilgileri yazdır
        print("\n📊 Oluşturulan Veriler:")
        print(f"- İstatistik kayıtları: {len(total_stats)} gün")
        print(f"- Telegram oturumları: {TelegramSession.query.filter_by(user_id=user.id).count()}")
        print(f"- Telegram grupları: {TelegramGroup.query.filter_by(user_id=user.id).count()}")
        print(f"- Kampanyalar: {Campaign.query.filter_by(user_id=user.id).count()}")
        print(f"- Toplam gönderilen davet: {user.total_invites_sent}")
        print(f"- Başarılı davetler: {user.successful_invites}")

if __name__ == "__main__":
    create_sample_data()