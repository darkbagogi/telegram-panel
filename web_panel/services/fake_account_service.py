#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sahte Hesap Raporlama Servisi
Web panel için modüler servis
"""

import sys
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from report_fake_account import FakeAccountReporter

class FakeAccountService:
    """Web panel için sahte hesap raporlama servisi"""
    
    def __init__(self, telegram_client):
        self.client = telegram_client
        self.reporter = FakeAccountReporter(telegram_client)
    
    async def report_account(self, username: str, reason: str = "spam") -> dict:
        """Hesabı raporla"""
        try:
            result = await self.reporter.report_fake_account(username, reason)
            
            return {
                'success': result['success'],
                'message': result.get('message', ''),
                'error': result.get('error', '')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def bulk_report(self, usernames: list, reason: str = "spam") -> dict:
        """Toplu raporlama"""
        try:
            results = []
            success_count = 0
            
            for username in usernames:
                result = await self.report_account(username, reason)
                results.append({
                    'username': username,
                    'success': result['success'],
                    'message': result.get('message', result.get('error', ''))
                })
                
                if result['success']:
                    success_count += 1
            
            return {
                'success': True,
                'total': len(usernames),
                'success_count': success_count,
                'failed_count': len(usernames) - success_count,
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
