#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Bilgi Sorgulama Servisi
Web panel için modüler servis
"""

import sys
from pathlib import Path

# Parent directory'yi path'e ekle
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from user_info_lookup import UserInfoLookup

class UserLookupService:
    """Web panel için kullanıcı sorgulama servisi"""
    
    def __init__(self, telegram_client):
        self.client = telegram_client
        self.lookup = UserInfoLookup(telegram_client)
    
    async def lookup_by_phone(self, phone_number: str) -> dict:
        """Telefon numarasından kullanıcı bilgisi"""
        try:
            result = await self.lookup.lookup_user_by_phone(phone_number)
            
            if result['success']:
                return {
                    'success': True,
                    'user': {
                        'id': result['user_id'],
                        'username': result['username'],
                        'first_name': result['first_name'],
                        'last_name': result['last_name'],
                        'phone': result['phone'],
                        'is_bot': result['is_bot'],
                        'is_premium': result['is_premium'],
                        'bio': result['bio'],
                        'photo_path': result['photo_path']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def lookup_by_username(self, username: str) -> dict:
        """Username'den kullanıcı bilgisi"""
        try:
            user = await self.client.get_entity(username)
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_bot': user.bot if hasattr(user, 'bot') else False,
                    'is_premium': user.premium if hasattr(user, 'premium') else False
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
