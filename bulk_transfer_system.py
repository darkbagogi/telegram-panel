#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Büyük Grup Toplu Aktarım Sistemi
Binlerce üyeli gruplar için güvenli aktarım
"""

import asyncio
import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from smart_inviter import SmartInviter, InviteResult



class BulkTransferSystem:
    """Büyük grup toplu aktarım sistemi"""
    
    def __init__(self, smart_inviter: SmartInviter):
        self.smart_inviter = smart_inviter
        self.transfer_queue = []
        self.completed_transfers = []
        self.failed_transfers = []
        
        # MAKSIMUM HIZ - 10 BİN KİŞİ İÇİN
        self.SAFE_DAILY_LIMIT = 10000   # Günlük limit
        self.SAFE_HOURLY_LIMIT = 10000  # Saatlik limit
        self.BATCH_SIZE = 50            # Her batch'te kaç kişi (artırıldı)
        self.BATCH_DELAY_MINUTES = 0    # Batch'ler arası bekleme YOK
        self.USER_DELAY_MIN_SECONDS = 0   # Kullanıcılar arası bekleme YOK
        self.USER_DELAY_MAX_SECONDS = 1   # Maksimum 1 saniye
        
    def calculate_transfer_plan(self, total_users: int) -> dict:
        """Aktarım planını yeni hız ayarlarına göre hesapla (dakika bazlı)."""
        if total_users == 0:
            return {
                'total_users': 0,
                'estimated_minutes': 0,
                'total_batches': 0,
                'users_per_batch': self.BATCH_SIZE
            }

        # Kullanıcı başına ortalama bekleme süresi (saniye)
        avg_user_delay = (self.USER_DELAY_MIN_SECONDS + self.USER_DELAY_MAX_SECONDS) / 2
        
        # Toplam kullanıcı davet süresi (saniye)
        total_user_delay_seconds = total_users * avg_user_delay
        
        # Toplam batch sayısı
        total_batches = math.ceil(total_users / self.BATCH_SIZE)
        
        # Toplam batch bekleme süresi (saniye)
        # İlk batch'ten sonra (total_batches - 1) kadar bekleme olur.
        total_batch_delay_seconds = (total_batches - 1) * self.BATCH_DELAY_MINUTES * 60
        if total_batch_delay_seconds < 0:
            total_batch_delay_seconds = 0

        # Toplam tahmini süre (saniye)
        total_seconds = total_user_delay_seconds + total_batch_delay_seconds
        
        # Dakikaya çevir
        estimated_minutes = math.ceil(total_seconds / 60)
        
        return {
            'total_users': total_users,
            'estimated_minutes': estimated_minutes,
            'total_batches': total_batches,
            'users_per_batch': self.BATCH_SIZE
        }
    
    def create_user_batches(self, users: List, criteria: Dict = None) -> List[List]:
        """Kullanıcıları batch'lere böl"""
        # Önce kullanıcıları filtrele
        if criteria:
            filtered_users = self.smart_inviter.filter_suitable_users(users, criteria)
        else:
            filtered_users = users
        
        # Batch'lere böl
        batches = []
        for i in range(0, len(filtered_users), self.BATCH_SIZE):
            batch = filtered_users[i:i + self.BATCH_SIZE]
            batches.append(batch)
        
        return batches

    def configure_from_mode(self, mode_config: Dict):
        """Sistemi seçilen moda göre yapılandırır."""
        self.SAFE_DAILY_LIMIT = mode_config.get('daily_limit', 40)
        self.SAFE_HOURLY_LIMIT = mode_config.get('hourly_limit', 8)
        self.BATCH_SIZE = mode_config.get('batch_size', 5)
        self.BATCH_DELAY_MINUTES = mode_config.get('batch_delay_minutes', 45)
        self.USER_DELAY_MIN_SECONDS = mode_config.get('min_delay_seconds', 30)
        self.USER_DELAY_MAX_SECONDS = mode_config.get('max_delay_seconds', 120)
        print(f"🔧 Aktarım modu ayarlandı: Kullanıcılar arası bekleme süresi {self.USER_DELAY_MIN_SECONDS}-{self.USER_DELAY_MAX_SECONDS} saniye olarak ayarlandı.")
    
    async def execute_bulk_transfer(self, users: List, target_group, 
                                  criteria: Dict = None, 
                                  auto_mode: bool = False) -> Dict:
        """Toplu aktarım gerçekleştir"""
        print(f"\n🚀 TOPLU AKTARIM BAŞLATIYOR")
        print("=" * 50)
        
        # Plan oluştur ve yazdır (isteğe bağlı)
        plan = self.calculate_transfer_plan(len(users))
        # self.print_transfer_plan(plan) # Kullanıcı onayı adımı kaldırıldı

        # Onay isteme adımı kaldırıldı
        # if not auto_mode:
        #     confirm = input(f"\n✅ Bu planla devam etmek istiyor musunuz? (e/h): ").lower()
        #     if confirm != 'e':
        #         print("❌ Aktarım iptal edildi.")
        #         return {'status': 'cancelled'}
        
        # Batch'leri oluştur
        batches = self.create_user_batches(users, criteria)
        
        print(f"\n📦 {plan['total_batches']} batch oluşturuldu")
        print(f"⏱️ Tahmini süre: Yaklaşık {plan['estimated_minutes']} dakika")
        
        # Aktarım istatistikleri
        transfer_stats = {
            'total_users': len(users),
            'total_batches': len(batches),
            'completed_batches': 0,
            'successful_invites': 0,
            'failed_invites': 0,
            'start_time': datetime.now(),
            'current_day': 1,
            'daily_invites': 0
        }
        
        # Batch'leri işle
        for batch_index, batch in enumerate(batches, 1):
            print(f"\n📦 Batch {batch_index}/{len(batches)} işleniyor...")
            
            # Günlük limit kontrolü
            if transfer_stats['daily_invites'] >= self.SAFE_DAILY_LIMIT:
                print(f"⏰ Günlük limit doldu. Yarın devam edilecek...")
                await self.wait_for_next_day()
                transfer_stats['current_day'] += 1
                transfer_stats['daily_invites'] = 0
            
            # Batch'i işle
            batch_results = await self.process_batch(batch, target_group, batch_index)
            
            # İstatistikleri güncelle
            transfer_stats['completed_batches'] += 1
            transfer_stats['successful_invites'] += batch_results['successful']
            transfer_stats['failed_invites'] += batch_results['failed']
            transfer_stats['daily_invites'] += batch_results['successful']
            
            # İlerleme raporu
            self.print_progress_report(transfer_stats, len(batches))
            
            # Batch'ler arası bekleme (son batch değilse)
            if batch_index < len(batches):
                await self.wait_between_batches()
        
        # Final rapor
        transfer_stats['end_time'] = datetime.now()
        transfer_stats['total_duration'] = transfer_stats['end_time'] - transfer_stats['start_time']
        
        self.print_final_report(transfer_stats)
        return transfer_stats
    
    async def process_batch(self, batch: List, target_group, batch_number: int) -> Dict:
        """Tek batch'i işle"""
        print(f"   👥 {len(batch)} kullanıcı davet ediliyor...")
        
        batch_stats = {
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for user in batch:
            try:
                # Botları ve kullanıcı adı olmayanları atla
                if user.get('is_bot') or not user.get('username'):
                    continue

                # Telethon için kullanıcı nesnesine dönüştür
                user_entity = await self.smart_inviter.client.get_entity(user['id'])

                # Kullanıcıyı davet et
                result = await self.smart_inviter.invite_user_to_group(
                    user_entity, target_group, f"Batch {batch_number}"
                )
                
                batch_stats['results'].append(result)
                
                if result.success:
                    batch_stats['successful'] += 1
                    print(f"   ✅ {result.username or result.user_id}")
                else:
                    batch_stats['failed'] += 1
                    print(f"   ❌ {result.username or result.user_id}: {result.error_type}")

            except Exception as e:
                batch_stats['failed'] += 1
                user_identifier = user.get('username') or user.get('id', 'Bilinmeyen Kullanıcı')
                print(f"   🔥 Batch içi hata ({user_identifier}): {e}")
                continue
            
            # Her kullanıcıdan sonra bekle
            await asyncio.sleep(random.randint(self.USER_DELAY_MIN_SECONDS, self.USER_DELAY_MAX_SECONDS))
        
        return batch_stats
    
    async def wait_between_batches(self):
        """Batch'ler arası bekleme"""
        wait_minutes = self.BATCH_DELAY_MINUTES
        print(f"⏳ Batch'ler arası bekleme: {wait_minutes} dakika...")
        
        # Dakika dakika geri sayım
        for minute in range(wait_minutes, 0, -1):
            print(f"   ⏰ {minute} dakika kaldı...", end='\r')
            await asyncio.sleep(60)
        
        print("   ✅ Bekleme tamamlandı!     ")
    
    async def wait_for_next_day(self):
        """Ertesi güne kadar bekle"""
        now = datetime.now()
        tomorrow = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_seconds = (tomorrow - now).total_seconds()
        
        print(f"🌙 Ertesi güne kadar bekleme: {wait_seconds/3600:.1f} saat")
        print(f"📅 Devam tarihi: {tomorrow.strftime('%d.%m.%Y %H:%M')}")
        
        await asyncio.sleep(wait_seconds)
    

    
    def print_progress_report(self, stats: Dict, total_batches: int):
        """İlerleme raporu"""
        progress = (stats['completed_batches'] / total_batches) * 100
        
        print(f"\n📊 İLERLEME RAPORU")
        print("=" * 25)
        print(f"📈 İlerleme: %{progress:.1f}")
        print(f"📦 Batch: {stats['completed_batches']}/{total_batches}")
        print(f"✅ Başarılı: {stats['successful_invites']}")
        print(f"❌ Başarısız: {stats['failed_invites']}")
        print(f"📅 Gün: {stats['current_day']}")
        print(f"📊 Günlük: {stats['daily_invites']}/{self.SAFE_DAILY_LIMIT}")
    
    def print_final_report(self, stats: Dict):
        """Final rapor"""
        success_rate = (stats['successful_invites'] / stats['total_users']) * 100
        duration_hours = stats['total_duration'].total_seconds() / 3600
        
        print(f"\n🎯 AKTARIM TAMAMLANDI!")
        print("=" * 35)
        print(f"👥 Toplam kullanıcı: {stats['total_users']:,}")
        print(f"✅ Başarılı davet: {stats['successful_invites']:,}")
        print(f"❌ Başarısız davet: {stats['failed_invites']:,}")
        print(f"📈 Başarı oranı: %{success_rate:.1f}")
        print(f"⏱️ Toplam süre: {duration_hours:.1f} saat")
        print(f"📦 İşlenen batch: {stats['completed_batches']}")
        print(f"📅 Tamamlanan gün: {stats['current_day']}")
        
        # Dosyaya kaydet
        self.save_transfer_report(stats)
    
    def save_transfer_report(self, stats: Dict):
        """Aktarım raporunu kaydet"""
        import os
        os.makedirs("reports", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/bulk_transfer_report_{timestamp}.json"
        
        # JSON serileştirilebilir hale getir
        report_data = {
            'total_users': stats['total_users'],
            'successful_invites': stats['successful_invites'],
            'failed_invites': stats['failed_invites'],
            'completed_batches': stats['completed_batches'],
            'start_time': stats['start_time'].isoformat(),
            'end_time': stats['end_time'].isoformat(),
            'total_duration_hours': stats['total_duration'].total_seconds() / 3600,
            'success_rate': (stats['successful_invites'] / stats['total_users']) * 100,
            'days_completed': stats['current_day']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Rapor kaydedildi: {filename}")