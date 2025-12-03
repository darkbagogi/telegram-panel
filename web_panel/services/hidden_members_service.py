#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gizli Üye Keşif Servisi
Web panel için modüler servis
"""

import sys
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from reveal_hidden_members import HiddenMemberRevealer

class HiddenMembersService:
    """Web panel için gizli üye keşif servisi"""
    
    def __init__(self, telegram_client):
        self.client = telegram_client
        self.revealer = HiddenMemberRevealer(telegram_client)
    
    async def reveal_members(self, group_link: str) -> dict:
        """Gizli üyeleri ortaya çıkar"""
        try:
            result = await self.revealer.reveal_hidden_members(group_link)
            
            return {
                'success': result['success'],
                'group_name': result.get('group_name', ''),
                'visible_count': result.get('visible_count', 0),
                'hidden_count': result.get('hidden_count', 0),
                'total_count': result.get('total_count', 0),
                'hidden_members': result.get('hidden_members', []),
                'error': result.get('error', '')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
