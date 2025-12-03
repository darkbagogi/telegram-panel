#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Üye Filtreleme Sistemi
Akıllı hedefleme ve filtreleme
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class FilterType(Enum):
    """Filtre türleri"""
    USERNAME = "username"
    PHONE = "phone"
    PREMIUM = "premium"
    ACTIVITY = "activity"
    PROFILE_PHOTO = "profile_photo"
    BIO = "bio"
    MUTUAL_CONTACTS = "mutual_contacts"
    LANGUAGE = "language"

@dataclass
class FilterCriteria:
    """Filtre kriterleri"""
    filter_type: FilterType
    value: any
    operator: str = "equals"  # equals, contains, greater_than, less_than, regex
    weight: float = 1.0  # Filtre ağırlığı (0-1)

class AdvancedMemberFilter:
    """Gelişmiş üye filtreleme sistemi"""
    
    def __init__(self):
        self.filters = []
        self.scoring_weights = {
            'username_quality': 0.2,
            'activity_score': 0.3,
            'profile_completeness': 0.2,
            'premium_status': 0.1,
            'mutual_contacts': 0.2
        }
    
    def add_filter(self, criteria: FilterCriteria):
        """Filtre ekle"""
        self.filters.append(criteria)
    
    def remove_filter(self, filter_type: FilterType):
        """Filtre kaldır"""
        self.filters = [f for f in self.filters if f.filter_type != filter_type]
    
    def clear_filters(self):
        """Tüm filtreleri temizle"""
        self.filters.clear()
    
    def apply_filters(self, users: List, strict_mode: bool = False) -> List:
        """Filtreleri uygula"""
        if not self.filters:
            return users
        
        filtered_users = []
        
        for user in users:
            if self._user_passes_filters(user, strict_mode):
                filtered_users.append(user)
        
        return filtered_users
    
    def _user_passes_filters(self, user, strict_mode: bool) -> bool:
        """Kullanıcı filtreleri geçiyor mu"""
        if strict_mode:
            # Sıkı mod: Tüm filtreler geçilmeli
            return all(self._apply_single_filter(user, filter_criteria) 
                      for filter_criteria in self.filters)
        else:
            # Esnek mod: Ağırlıklı puanlama
            total_weight = sum(f.weight for f in self.filters)
            if total_weight == 0:
                return True
            
            passed_weight = sum(f.weight for f in self.filters 
                              if self._apply_single_filter(user, f))
            
            return (passed_weight / total_weight) >= 0.6  # %60 eşik
    
    def _apply_single_filter(self, user, criteria: FilterCriteria) -> bool:
        """Tek filtre uygula"""
        try:
            if criteria.filter_type == FilterType.USERNAME:
                return self._filter_username(user, criteria)
            elif criteria.filter_type == FilterType.PHONE:
                return self._filter_phone(user, criteria)
            elif criteria.filter_type == FilterType.PREMIUM:
                return self._filter_premium(user, criteria)
            elif criteria.filter_type == FilterType.ACTIVITY:
                return self._filter_activity(user, criteria)
            elif criteria.filter_type == FilterType.PROFILE_PHOTO:
                return self._filter_profile_photo(user, criteria)
            elif criteria.filter_type == FilterType.BIO:
                return self._filter_bio(user, criteria)
            elif criteria.filter_type == FilterType.MUTUAL_CONTACTS:
                return self._filter_mutual_contacts(user, criteria)
            elif criteria.filter_type == FilterType.LANGUAGE:
                return self._filter_language(user, criteria)
        except Exception:
            return False
        
        return True
    
    def _filter_username(self, user, criteria: FilterCriteria) -> bool:
        """Kullanıcı adı filtresi"""
        username = getattr(user, 'username', None)
        
        if criteria.operator == "exists":
            return username is not None and username != ""
        elif criteria.operator == "not_exists":
            return username is None or username == ""
        elif criteria.operator == "contains" and username:
            return criteria.value.lower() in username.lower()
        elif criteria.operator == "regex" and username:
            return bool(re.search(criteria.value, username, re.IGNORECASE))
        elif criteria.operator == "min_length" and username:
            return len(username) >= criteria.value
        
        return True
    
    def _filter_phone(self, user, criteria: FilterCriteria) -> bool:
        """Telefon filtresi"""
        phone = getattr(user, 'phone', None)
        
        if criteria.operator == "exists":
            return phone is not None and phone != ""
        elif criteria.operator == "not_exists":
            return phone is None or phone == ""
        elif criteria.operator == "country_code" and phone:
            return phone.startswith(str(criteria.value))
        
        return True
    
    def _filter_premium(self, user, criteria: FilterCriteria) -> bool:
        """Premium filtresi"""
        is_premium = getattr(user, 'premium', False)
        
        if criteria.operator == "equals":
            return is_premium == criteria.value
        
        return True
    
    def _filter_activity(self, user, criteria: FilterCriteria) -> bool:
        """Aktivite filtresi"""
        if not hasattr(user, 'status'):
            return False
        
        status = user.status
        
        if criteria.operator == "online":
            return hasattr(status, 'was_online') or str(status) == "UserStatusOnline"
        elif criteria.operator == "recently_active":
            if hasattr(status, 'was_online'):
                last_seen = status.was_online
                days_ago = (datetime.now() - last_seen).days
                return days_ago <= criteria.value
        elif criteria.operator == "not_long_ago":
            if hasattr(status, 'was_online'):
                last_seen = status.was_online
                days_ago = (datetime.now() - last_seen).days
                return days_ago <= 30  # Son 30 gün
        
        return True
    
    def _filter_profile_photo(self, user, criteria: FilterCriteria) -> bool:
        """Profil fotoğrafı filtresi"""
        has_photo = getattr(user, 'photo', None) is not None
        
        if criteria.operator == "exists":
            return has_photo == criteria.value
        
        return True
    
    def _filter_bio(self, user, criteria: FilterCriteria) -> bool:
        """Bio filtresi"""
        # Bu özellik için ek API çağrısı gerekebilir
        # Şimdilik basit kontrol
        return True
    
    def _filter_mutual_contacts(self, user, criteria: FilterCriteria) -> bool:
        """Karşılıklı kontak filtresi"""
        is_mutual = getattr(user, 'mutual_contact', False)
        
        if criteria.operator == "equals":
            return is_mutual == criteria.value
        
        return True
    
    def _filter_language(self, user, criteria: FilterCriteria) -> bool:
        """Dil filtresi"""
        lang_code = getattr(user, 'lang_code', None)
        
        if criteria.operator == "equals" and lang_code:
            return lang_code == criteria.value
        elif criteria.operator == "in_list" and lang_code:
            return lang_code in criteria.value
        
        return True
    
    def calculate_user_score(self, user) -> float:
        """Kullanıcı puanı hesapla"""
        score = 0.0
        
        # Kullanıcı adı kalitesi
        username_score = self._calculate_username_score(user)
        score += username_score * self.scoring_weights['username_quality']
        
        # Aktivite puanı
        activity_score = self._calculate_activity_score(user)
        score += activity_score * self.scoring_weights['activity_score']
        
        # Profil tamamlanma puanı
        profile_score = self._calculate_profile_completeness(user)
        score += profile_score * self.scoring_weights['profile_completeness']
        
        # Premium durumu
        premium_score = 1.0 if getattr(user, 'premium', False) else 0.0
        score += premium_score * self.scoring_weights['premium_status']
        
        # Karşılıklı kontak
        mutual_score = 1.0 if getattr(user, 'mutual_contact', False) else 0.0
        score += mutual_score * self.scoring_weights['mutual_contacts']
        
        return min(score, 1.0)  # 0-1 arası sınırla
    
    def _calculate_username_score(self, user) -> float:
        """Kullanıcı adı puanı"""
        username = getattr(user, 'username', None)
        
        if not username:
            return 0.0
        
        score = 0.5  # Temel puan
        
        # Uzunluk kontrolü
        if len(username) >= 5:
            score += 0.2
        
        # Sayı oranı kontrolü
        digit_ratio = sum(c.isdigit() for c in username) / len(username)
        if digit_ratio < 0.5:  # %50'den az sayı
            score += 0.2
        
        # Özel karakter kontrolü
        if not re.search(r'[_\d]{3,}', username):  # Çok fazla alt çizgi/sayı yok
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_activity_score(self, user) -> float:
        """Aktivite puanı"""
        if not hasattr(user, 'status'):
            return 0.0
        
        status = user.status
        
        if str(status) == "UserStatusOnline":
            return 1.0
        elif hasattr(status, 'was_online'):
            last_seen = status.was_online
            days_ago = (datetime.now() - last_seen).days
            
            if days_ago <= 1:
                return 0.9
            elif days_ago <= 7:
                return 0.7
            elif days_ago <= 30:
                return 0.5
            else:
                return 0.2
        
        return 0.3  # Bilinmeyen durum
    
    def _calculate_profile_completeness(self, user) -> float:
        """Profil tamamlanma puanı"""
        score = 0.0
        
        # İsim kontrolü
        if getattr(user, 'first_name', None):
            score += 0.3
        
        if getattr(user, 'last_name', None):
            score += 0.2
        
        # Kullanıcı adı
        if getattr(user, 'username', None):
            score += 0.3
        
        # Profil fotoğrafı
        if getattr(user, 'photo', None):
            score += 0.2
        
        return min(score, 1.0)
    
    def rank_users_by_score(self, users: List) -> List:
        """Kullanıcıları puana göre sırala"""
        user_scores = []
        
        for user in users:
            score = self.calculate_user_score(user)
            user_scores.append((user, score))
        
        # Puana göre azalan sırada sırala
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [user for user, score in user_scores]
    
    def get_filter_statistics(self, users: List) -> Dict:
        """Filtre istatistikleri"""
        stats = {
            'total_users': len(users),
            'filtered_users': 0,
            'filter_breakdown': {},
            'score_distribution': {
                'high_quality': 0,    # 0.8+
                'medium_quality': 0,  # 0.5-0.8
                'low_quality': 0      # <0.5
            }
        }
        
        filtered_users = self.apply_filters(users)
        stats['filtered_users'] = len(filtered_users)
        
        # Filtre detayları
        for filter_criteria in self.filters:
            filter_name = f"{filter_criteria.filter_type.value}_{filter_criteria.operator}"
            passed_count = sum(1 for user in users 
                             if self._apply_single_filter(user, filter_criteria))
            stats['filter_breakdown'][filter_name] = {
                'passed': passed_count,
                'percentage': (passed_count / len(users) * 100) if users else 0
            }
        
        # Puan dağılımı
        for user in users:
            score = self.calculate_user_score(user)
            if score >= 0.8:
                stats['score_distribution']['high_quality'] += 1
            elif score >= 0.5:
                stats['score_distribution']['medium_quality'] += 1
            else:
                stats['score_distribution']['low_quality'] += 1
        
        return stats

class PresetFilters:
    """Hazır filtre setleri"""
    
    @staticmethod
    def high_quality_users() -> List[FilterCriteria]:
        """Yüksek kalite kullanıcılar"""
        return [
            FilterCriteria(FilterType.USERNAME, True, "exists", 0.8),
            FilterCriteria(FilterType.PREMIUM, True, "equals", 0.6),
            FilterCriteria(FilterType.ACTIVITY, 7, "recently_active", 0.9),
            FilterCriteria(FilterType.PROFILE_PHOTO, True, "exists", 0.5)
        ]
    
    @staticmethod
    def active_users() -> List[FilterCriteria]:
        """Aktif kullanıcılar"""
        return [
            FilterCriteria(FilterType.ACTIVITY, 30, "recently_active", 1.0)
        ]
    
    @staticmethod
    def premium_users() -> List[FilterCriteria]:
        """Premium kullanıcılar"""
        return [
            FilterCriteria(FilterType.PREMIUM, True, "equals", 1.0)
        ]
    
    @staticmethod
    def users_with_username() -> List[FilterCriteria]:
        """Kullanıcı adı olan kullanıcılar"""
        return [
            FilterCriteria(FilterType.USERNAME, True, "exists", 1.0),
            FilterCriteria(FilterType.USERNAME, 4, "min_length", 0.5)
        ]
    
    @staticmethod
    def turkish_users() -> List[FilterCriteria]:
        """Türk kullanıcılar"""
        return [
            FilterCriteria(FilterType.LANGUAGE, "tr", "equals", 0.8),
            FilterCriteria(FilterType.PHONE, "90", "country_code", 0.6)
        ]

if __name__ == "__main__":
    print("Gelişmiş Üye Filtreleme Sistemi")
    print("Bu modül main.py üzerinden kullanılmalıdır.")