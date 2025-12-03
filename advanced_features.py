#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Özellikler Modülü
Başarı takibi, raporlama ve analitik
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass

@dataclass
class CampaignMetrics:
    """Kampanya metrikleri"""
    campaign_id: str
    start_time: datetime
    end_time: datetime
    total_attempts: int
    successful_invites: int
    success_rate: float
    avg_delay: float
    errors: Dict[str, int]

class AnalyticsEngine:
    """Analitik motoru"""
    
    def __init__(self, data_dir: str = "analytics"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_campaign_data(self, campaign_data: Dict):
        """Kampanya verilerini kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/campaign_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(campaign_data, f, ensure_ascii=False, indent=2)
    
    def load_all_campaigns(self) -> List[Dict]:
        """Tüm kampanya verilerini yükle"""
        campaigns = []
        
        for filename in os.listdir(self.data_dir):
            if filename.startswith('campaign_') and filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        campaigns.append(json.load(f))
                except Exception as e:
                    print(f"Dosya okunamadı {filename}: {e}")
        
        return campaigns
    
    def generate_success_report(self) -> Dict:
        """Başarı raporu oluştur"""
        campaigns = self.load_all_campaigns()
        
        if not campaigns:
            return {"error": "Kampanya verisi bulunamadı"}
        
        total_attempts = sum(c.get('stats', {}).get('total_attempts', 0) for c in campaigns)
        total_success = sum(c.get('stats', {}).get('successful_invites', 0) for c in campaigns)
        
        # Hata analizi
        error_analysis = {}
        for campaign in campaigns:
            for result in campaign.get('results', []):
                if not result.get('success', False):
                    error_type = result.get('error_type', 'unknown')
                    error_analysis[error_type] = error_analysis.get(error_type, 0) + 1
        
        # Zaman analizi
        daily_stats = self.get_daily_statistics(campaigns)
        
        return {
            'overview': {
                'total_campaigns': len(campaigns),
                'total_attempts': total_attempts,
                'total_successful': total_success,
                'overall_success_rate': (total_success / total_attempts * 100) if total_attempts > 0 else 0
            },
            'error_analysis': error_analysis,
            'daily_statistics': daily_stats,
            'recommendations': self.generate_recommendations(campaigns)
        }
    
    def get_daily_statistics(self, campaigns: List[Dict]) -> Dict:
        """Günlük istatistikler"""
        daily_data = {}
        
        for campaign in campaigns:
            campaign_date = campaign.get('campaign_date', '')
            if campaign_date:
                try:
                    date = datetime.fromisoformat(campaign_date).date()
                    date_str = date.isoformat()
                    
                    if date_str not in daily_data:
                        daily_data[date_str] = {
                            'attempts': 0,
                            'successful': 0,
                            'campaigns': 0
                        }
                    
                    daily_data[date_str]['attempts'] += campaign.get('stats', {}).get('total_attempts', 0)
                    daily_data[date_str]['successful'] += campaign.get('stats', {}).get('successful_invites', 0)
                    daily_data[date_str]['campaigns'] += 1
                except:
                    continue
        
        # Başarı oranlarını hesapla
        for date_str in daily_data:
            attempts = daily_data[date_str]['attempts']
            successful = daily_data[date_str]['successful']
            daily_data[date_str]['success_rate'] = (successful / attempts * 100) if attempts > 0 else 0
        
        return daily_data
    
    def generate_recommendations(self, campaigns: List[Dict]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        if not campaigns:
            return ["Henüz kampanya verisi yok"]
        
        # Başarı oranı analizi
        total_attempts = sum(c.get('stats', {}).get('total_attempts', 0) for c in campaigns)
        total_success = sum(c.get('stats', {}).get('successful_invites', 0) for c in campaigns)
        success_rate = (total_success / total_attempts * 100) if total_attempts > 0 else 0
        
        if success_rate < 30:
            recommendations.append("⚠️ Düşük başarı oranı: Hedef grup seçimini gözden geçirin")
            recommendations.append("💡 Daha aktif kullanıcıları hedefleyin")
        elif success_rate > 70:
            recommendations.append("✅ Yüksek başarı oranı: Mevcut stratejiyi sürdürün")
        
        # Hata analizi
        error_counts = {}
        for campaign in campaigns:
            for result in campaign.get('results', []):
                if not result.get('success', False):
                    error_type = result.get('error_type', 'unknown')
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        if error_counts.get('privacy_restricted', 0) > total_attempts * 0.3:
            recommendations.append("🔒 Çok fazla gizlilik kısıtlaması: Daha açık profilli kullanıcıları hedefleyin")
        
        if error_counts.get('flood_wait', 0) > 5:
            recommendations.append("⏰ Çok fazla rate limit: Gecikme sürelerini artırın")
        
        return recommendations
    
    def export_to_csv(self, filename: str = None):
        """CSV'ye aktar"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.data_dir}/analytics_export_{timestamp}.csv"
        
        campaigns = self.load_all_campaigns()
        
        # CSV için veri hazırla
        csv_data = []
        for campaign in campaigns:
            for result in campaign.get('results', []):
                csv_data.append({
                    'campaign_date': campaign.get('campaign_date', ''),
                    'user_id': result.get('user_id', ''),
                    'username': result.get('username', ''),
                    'success': result.get('success', False),
                    'error_type': result.get('error_type', ''),
                    'error_message': result.get('error_message', ''),
                    'timestamp': result.get('timestamp', '')
                })
        
        # CSV'ye yaz
        if csv_data:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"📊 Analitik veriler CSV'ye aktarıldı: {filename}")
        else:
            print("❌ Aktarılacak veri bulunamadı")

class PerformanceTracker:
    """Performans takipçisi"""
    
    def __init__(self):
        self.metrics = {
            'daily_limits': {},
            'success_trends': {},
            'error_patterns': {},
            'optimal_times': {}
        }
    
    def track_daily_performance(self, date: str, attempts: int, success: int):
        """Günlük performans takibi"""
        if date not in self.metrics['daily_limits']:
            self.metrics['daily_limits'][date] = {
                'attempts': 0,
                'success': 0,
                'limit_reached': False
            }
        
        self.metrics['daily_limits'][date]['attempts'] += attempts
        self.metrics['daily_limits'][date]['success'] += success
        
        # Günlük limit kontrolü
        if attempts >= 50:  # Günlük limit
            self.metrics['daily_limits'][date]['limit_reached'] = True
    
    def analyze_optimal_times(self, campaigns: List[Dict]) -> Dict:
        """Optimal zamanları analiz et"""
        hourly_success = {}
        
        for campaign in campaigns:
            for result in campaign.get('results', []):
                timestamp_str = result.get('timestamp', '')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        hour = timestamp.hour
                        
                        if hour not in hourly_success:
                            hourly_success[hour] = {'attempts': 0, 'success': 0}
                        
                        hourly_success[hour]['attempts'] += 1
                        if result.get('success', False):
                            hourly_success[hour]['success'] += 1
                    except:
                        continue
        
        # Başarı oranlarını hesapla
        optimal_hours = {}
        for hour, data in hourly_success.items():
            if data['attempts'] > 0:
                success_rate = data['success'] / data['attempts'] * 100
                optimal_hours[hour] = {
                    'success_rate': success_rate,
                    'attempts': data['attempts']
                }
        
        return optimal_hours
    
    def get_performance_summary(self) -> Dict:
        """Performans özeti"""
        return {
            'daily_performance': self.metrics['daily_limits'],
            'success_trends': self.metrics['success_trends'],
            'recommendations': self.generate_performance_recommendations()
        }
    
    def generate_performance_recommendations(self) -> List[str]:
        """Performans önerileri"""
        recommendations = []
        
        # Günlük limit analizi
        recent_days = list(self.metrics['daily_limits'].keys())[-7:]  # Son 7 gün
        limit_reached_days = sum(1 for day in recent_days 
                               if self.metrics['daily_limits'].get(day, {}).get('limit_reached', False))
        
        if limit_reached_days > 3:
            recommendations.append("⚠️ Sık sık günlük limite ulaşıyorsunuz - daha az agresif strateji deneyin")
        
        return recommendations

class ReportGenerator:
    """Rapor oluşturucu"""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics = analytics_engine
    
    def generate_weekly_report(self) -> str:
        """Haftalık rapor oluştur"""
        report = self.analytics.generate_success_report()
        
        report_text = f"""
📊 HAFTALIK PERFORMANS RAPORU
{'=' * 50}

📈 GENEL ÖZET:
• Toplam kampanya: {report['overview']['total_campaigns']}
• Toplam deneme: {report['overview']['total_attempts']}
• Başarılı davet: {report['overview']['total_successful']}
• Genel başarı oranı: {report['overview']['overall_success_rate']:.1f}%

❌ HATA ANALİZİ:
"""
        
        for error_type, count in report['error_analysis'].items():
            report_text += f"• {error_type}: {count}\n"
        
        report_text += f"\n💡 ÖNERİLER:\n"
        for recommendation in report['recommendations']:
            report_text += f"• {recommendation}\n"
        
        return report_text
    
    def save_report(self, report_text: str, filename: str = None):
        """Raporu dosyaya kaydet"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/weekly_report_{timestamp}.txt"
        
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"📄 Rapor kaydedildi: {filename}")

if __name__ == "__main__":
    print("Gelişmiş Özellikler Modülü")
    print("Bu modül main.py üzerinden kullanılmalıdır.")