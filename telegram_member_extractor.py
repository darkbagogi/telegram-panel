import asyncio
import csv
import json
from telethon import TelegramClient

class TelegramMemberExtractor:
    def __init__(self, api_id, api_hash, phone):
        self.client = TelegramClient(phone, api_id, api_hash)
        self.members = []

    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(phone)
            await self.client.sign_in(phone, input('Enter the code: '))

    async def disconnect(self):
        await self.client.disconnect()

    async def get_group_members(self, group_username, limit=None):
        group = await self.client.get_entity(group_username)
        self.members = await self.client.get_participants(group, limit=limit)
        return self.members

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'first_name', 'last_name', 'username', 'phone'])
            for member in self.members:
                writer.writerow([member.id, member.first_name, member.last_name, member.username, member.phone])

    def save_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([
                {
                    'id': member.id,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'username': member.username,
                    'phone': member.phone
                } for member in self.members
            ], f, ensure_ascii=False, indent=4)

    def filter_members(self, has_username=False, has_phone=False, is_premium=False, first_name=None):
        filtered = self.members
        if has_username:
            filtered = [m for m in filtered if m.username]
        if has_phone:
            filtered = [m for m in filtered if m.phone]
        if is_premium:
            filtered = [m for m in filtered if m.premium]
        if first_name:
            filtered = [m for m in filtered if m.first_name and first_name.lower() in m.first_name.lower()]
        return filtered

    def get_statistics(self):
        total_members = len(self.members)
        with_username = len([m for m in self.members if m.username])
        premium_users = len([m for m in self.members if m.premium])
        return {
            'total_members': total_members,
            'with_username': with_username,
            'premium_users': premium_users
        }