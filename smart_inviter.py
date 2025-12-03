#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akıllı Telegram Üye Davet Sistemi
Spam koruması ile güvenli üye çekme
"""

import asyncio
import random
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import (
    FloodWaitError, UserPrivacyRestrictedError, UserNotMutualContactError,
    UserChannelsTooMuchError, ChatAdminRequiredError, UserBannedInChannelError,
    PeerFloodError, UserAlreadyParticipantError
)

@dataclass
class InviteResult:
    """Davet sonucu"""
    user_id: int
    username: str
    success: bool
    error_type: str = ""
    error_message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SmartInviter:
    """Akıllı üye davet sistemi"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.invite_results = []
        self.daily_invite_count = 0
        self.last_invite_time = None
        self.flood_wait_until = None
        
        # Güvenlik limitleri - MAKSIMUM HIZ
        self.MAX_DAILY_INVITES = 10000  # Günlük maksimum davet
        self.MAX_HOURLY_INVITES = 1000  # Saatlik maksimum davet
        self.MIN_DELAY_SECONDS = 1      # Minimum bekleme süresi
        self.MAX_DELAY_SECONDS = 2      # Maksimum bekleme süresi
        
        # İstatistikler
        self.stats = {
            'total_attempts': 0,
            'successful_invites': 0,
            'failed_invites': 0,
            'privacy_restricted': 0,
            'already_member': 0,
            'flood_waits': 0,
            'banned_users': 0
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Loglama ayarları"""
        self.logger = logging.getLogger('SmartInviter')
        handler = logging.FileHandler('logs/smart_inviter.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def can_invite_now(self) -> Tuple[bool, str]:
        """Şu anda davet yapılabilir mi kontrol et"""
        now = datetime.now()
        
        # Flood wait kontrolü
        if self.flood_wait_until and now < self.flood_wait_until:
            remaining = (self.flood_wait_until - now).seconds
            return False, f"Flood wait aktif: {remaining} saniye kaldı"
        
        # Günlük limit kontrolü
        if self.daily_invite_count >= self.MAX_DAILY_INVITES:
            return False, f"Günlük limit aşıldı: {self.daily_invite_count}/{self.MAX_DAILY_INVITES}"
        
        # Son davet zamanı kontrolü
        if self.last_invite_time:
            time_since_last = (now - self.last_invite_time).seconds
            if time_since_last < self.MIN_DELAY_SECONDS:
                wait_time = self.MIN_DELAY_SECONDS - time_since_last
                return False, f"Çok erken: {wait_time} saniye bekleyin"
        
        return True, "Davet yapılabilir"
    
    def calculate_smart_delay(self) -> int:
        """Akıllı gecikme hesapla"""
        base_delay = random.randint(self.MIN_DELAY_SECONDS, self.MAX_DELAY_SECONDS)
        
        # Başarı oranına göre gecikme ayarla
        if self.stats['total_attempts'] > 0:
            success_rate = self.stats['successful_invites'] / self.stats['total_attempts']
            if success_rate < 0.3:  # Düşük başarı oranı
                base_delay *= 2  # Gecikmeyi artır
            elif success_rate > 0.7:  # Yüksek başarı oranı
                base_delay = int(base_delay * 0.8)  # Gecikmeyi azalt
        
        # Flood wait geçmişine göre ayarla
        if self.stats['flood_waits'] > 3:
            base_delay *= 1.5
        
        return base_delay
    
    async def invite_user_to_group(self, user, target_group, source_group_name: str = "") -> InviteResult:
        """Kullanıcıyı gruba davet et"""
        user_id = user.id
        username = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        self.stats['total_attempts'] += 1
        
        try:
            # Kullanıcının zaten üye olup olmadığını kontrol et
            try:
                participants = await self.client.get_participants(target_group, limit=1)
                if any(p.id == user_id for p in participants):
                    result = InviteResult(user_id, username, False, "already_member", "Kullanıcı zaten üye")
                    self.stats['already_member'] += 1
                    return result
            except:
                pass  # Kontrol edilemezse devam et
            
            # Davet işlemi
            if hasattr(target_group, 'megagroup') and target_group.megagroup:
                # Süper grup için
                await self.client(InviteToChannelRequest(target_group, [user]))
            else:
                # Normal grup için
                await self.client(AddChatUserRequest(target_group.id, user_id, fwd_limit=10))
            
            # Başarılı davet
            self.stats['successful_invites'] += 1
            self.daily_invite_count += 1
            self.last_invite_time = datetime.now()
            
            result = InviteResult(user_id, username, True)
            self.logger.info(f"Başarılı davet: {username} ({user_id}) -> {target_group.title}")
            
            return result
            
        except FloodWaitError as e:
            # Rate limit - Atla ve devam et
            self.stats['flood_waits'] += 1
            self.logger.warning(f"Flood wait atlandı: {username} (orijinal: {e.seconds}s)")
            print(f"⚠️ Flood wait atlandı: {username}")
            result = InviteResult(user_id, username, False, "flood_wait", f"Flood wait: {e.seconds}s")
            return result
            
        except UserPrivacyRestrictedError:
            # Gizlilik ayarları
            self.stats['privacy_restricted'] += 1
            result = InviteResult(user_id, username, False, "privacy_restricted", "Gizlilik ayarları")
            return result
            
        except UserNotMutualContactError:
            result = InviteResult(user_id, username, False, "not_mutual_contact", "Karşılıklı kontak değil")
            return result
            
        except UserChannelsTooMuchError:
            result = InviteResult(user_id, username, False, "too_many_channels", "Çok fazla kanal/grup")
            return result
            
        except UserBannedInChannelError:
            self.stats['banned_users'] += 1
            result = InviteResult(user_id, username, False, "banned", "Kullanıcı yasaklı")
            return result
            
        except UserAlreadyParticipantError:
            self.stats['already_member'] += 1
            result = InviteResult(user_id, username, False, "already_member", "Zaten üye")
            return result
            
        except ChatAdminRequiredError:
            result = InviteResult(user_id, username, False, "admin_required", "Admin yetkisi gerekli")
            return result
            
        except PeerFloodError:
            result = InviteResult(user_id, username, False, "peer_flood", "Çok fazla istek")
            return result
            
        except Exception as e:
            self.stats['failed_invites'] += 1
            error_msg = f"{type(e).__name__}: {str(e)}"
            result = InviteResult(user_id, username, False, "unknown_error"
            return result
    
    def filter_suitable_users(self, users: List, criteria: Dict = None) -> List:
        """Davet için uygun kullanıcıları filtrele"""
        if criteria is None:
            criteria = {}
        
        suitable_users = []
        
        for user in users:
            # Bot kontrolü
            if getattr(user, 'bot', False):
                continue
            
            # Deleted account kontrolü
            if getattr(user, 'deleted', False):
                continue
            
            # Username kontrolü
            if criteria.get('require_username', False) and not user.username:
                continue
            
            # Premium kontrolü
            if criteria.get('premium_only', False) and not getattr(user, 'premium', False):
                continue
            
            # Son görülme kontrolü
            if criteria.get('active_recently', False):
                # Son 30 gün içinde aktif olanlar
                if hasattr(user, 'status') and hasattr(user.status, 'was_online'):
                    last_seen = user.status.was_online
                    if (datetime.now() - last_seen).days > 30:
                        continue
            
            suitable_users.append(user)
        
        return suitable_users
    
    async def smart_invite_campaign(self, source_users: List, target_group, 
                                  max_invites: int = 20, criteria: Dict = None) -> Dict:
        """Akıllı davet kampanyası"""
        
        print(f"\n🎯 Akıllı Davet Kampanyası Başlatılıyor")
        print(f"Hedef grup: {target_group.title}")
        print(f"Maksimum davet: {max_invites}")
        print("=" * 50)
        
        # Uygun kullanıcıları filtrele
        suitable_users = self.filter_suitable_users(source_users, criteria)
        print(f"✅ {len(suitable_users)} uygun kullanıcı bulundu")
        
        # Kullanıcıları karıştır (doğal görünmesi için)
        random.shuffle(suitable_users)
        
        invited_count = 0
        results = []
        
        for i, user in enumerate(suitable_users[:max_invites], 1):
            # Davet kontrolü
            can_invite, reason = self.can_invite_now()
            if not can_invite:
                print(f"⏸️  Davet durdu: {reason}")
                if "Flood wait" in reason:
                    # Flood wait durumunda bekle
                    wait_time = int(reason.split(":")[1].split()[0])
                    print(f"⏳ {wait_time} saniye bekleniyor...")
                    await asyncio.sleep(wait_time + 5)
                    continue
                else:
                    break
            
            # Kullanıcıyı davet et
            print(f"📤 [{i}/{max_invites}] Davet ediliyor: {user.username or user.first_name}")
            
            result = await self.invite_user_to_group(user, target_group)
            results.append(result)
            
            if result.success:
                invited_count += 1
                print(f"✅ Başarılı: {result.username}")
            else:
                print(f"❌ Başarısız: {result.username} - {result.error_message}")
            
            # Akıllı gecikme
            if i < len(suitable_users):
                delay = self.calculate_smart_delay()
                print(f"⏳ {delay} saniye bekleniyor...")
                await asyncio.sleep(delay)
        
        # Sonuçları kaydet
        self.invite_results.extend(results)
        
        # Özet rapor
        campaign_stats = {
            'total_attempts': len(results),
            'successful_invites': invited_count,
            'success_rate': (invited_count / len(results) * 100) if results else 0,
            'results': results
        }
        
        self.print_campaign_summary(campaign_stats)
        return campaign_stats
    
    def print_campaign_summary(self, campaign_stats: Dict):
        """Kampanya özeti yazdır"""
        print(f"\n📊 Kampanya Özeti")
        print("=" * 30)
        print(f"Toplam deneme: {campaign_stats['total_attempts']}")
        print(f"Başarılı davet: {campaign_stats['successful_invites']}")
        print(f"Başarı oranı: {campaign_stats['success_rate']:.1f}%")
        
        # Hata türleri
        error_counts = {}
        for result in campaign_stats['results']:
            if not result.success:
                error_type = result.error_type
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        if error_counts:
            print(f"\n❌ Hata Türleri:")
            for error_type, count in error_counts.items():
                print(f"  - {error_type}: {count}")
    
    def save_results_to_file(self, filename: str = None):
        """Sonuçları dosyaya kaydet"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/invite_results_{timestamp}.json"
        
        data = {
            'campaign_date': datetime.now().isoformat(),
            'stats': self.stats,
            'results': [
                {
                    'user_id': r.user_id,
                    'username': r.username,
                    'success': r.success,
                    'error_type': r.error_type,
                    'error_message': r.error_message,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.invite_results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Sonuçlar kaydedildi: {filename}")
    
    def get_daily_stats(self) -> Dict:
        """Günlük istatistikler"""
        today = datetime.now().date()
        today_results = [r for r in self.invite_results if r.timestamp.date() == today]
        
        return {
            'date': today.isoformat(),
            'total_invites_today': len(today_results),
            'successful_today': len([r for r in today_results if r.success]),
            'remaining_daily_limit': self.MAX_DAILY_INVITES - self.daily_invite_count,
            'success_rate_today': (len([r for r in today_results if r.success]) / len(today_results) * 100) if today_results else 0
        }

class InviteCriteria:
    """Davet kriterleri yardımcı sınıfı"""
    
    @staticmethod
    def active_users():
        """Aktif kullanıcılar"""
        return {'active_recently': True}
    
    @staticmethod
    def premium_users():
        """Premium kullanıcılar"""
        return {'premium_only': True}
    
    @staticmethod
    def users_with_username():
        """Kullanıcı adı olan kullanıcılar"""
        return {'require_username': True}
    
    @staticmethod
    def high_quality_users():
        """Yüksek kalite kullanıcılar"""
        return {
            'require_username': True,
            'active_recently': True
        }

if __name__ == "__main__":
    print("Akıllı Telegram Üye Davet Sistemi")
    print("Bu modül main.py üzerinden kullanılmalıdır.")