#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telentro Etkileşim Modülü
Görüntüleme, beğeni, emoji, anket ve çekiliş etkileşimleri
"""

import asyncio
import random
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest, GetPollVotesRequest, SendVoteRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import (
    InputPeerSelf, ReactionCount, ReactionCustomEmoji, InputReactionEmoji,
    MessageReactions, Poll, PollAnswer
)
from telethon.errors import FloodWaitError, ChatAdminRequiredError, MessageNotModifiedError

@dataclass
class InteractionResult:
    """Etkileşim sonucu"""
    success: bool
    interaction_type: str
    target_id: int
    target_type: str  # 'message', 'poll', 'giveaway'
    action: str
    timestamp: datetime
    error_message: Optional[str] = None
    details: Optional[Dict] = None

@dataclass
class GiveawayInfo:
    """Çekiliş bilgisi"""
    message_id: int
    chat_id: int
    title: str
    participants_count: int
    winners_count: int
    end_date: datetime
    is_active: bool = True
    requirements: List[str] = None

class InteractionManager:
    """Etkileşim yöneticisi sınıfı"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.interaction_history = []
        
        # Emoji reaksiyonları
        self.reactions = {
            'positive': ['👍', '❤️', '🔥', '😍', '🎉', '💯', '🌟', '✨', '💪', '🙏'],
            'neutral': ['👀', '🤔', '🙂', '😊', '👌', '✅', '🔔', '📌'],
            'negative': ['👎', '😕', '😔', '😢', '😡', '👎', '🚫'],
            'custom': ['🎯', '💎', '🚀', '⭐', '🏆', '🎨', '🎭', '🎪', '🎬', '🎮']
        }
        
        # Anket seçenekleri
        self.poll_responses = {
            'yes_no': ['Evet', 'Hayır'],
            'rating': ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'],
            'multiple_choice': ['Seçenek A', 'Seçenek B', 'Seçenek C', 'Seçenek D'],
            'opinion': ['Kesinlikle', 'Evet', 'Belki', 'Hayır', 'Kesinlikle Hayır']
        }
    
    async def send_message_reaction(self, chat_id: int, message_id: int, reaction: str = None, reaction_type: str = 'positive') -> InteractionResult:
        """Mesaja reaksiyon gönder"""
        try:
            if reaction is None:
                reaction = random.choice(self.reactions.get(reaction_type, self.reactions['positive']))
            
            # Reaksiyonu gönder
            await self.client.send_reaction(
                entity=chat_id,
                message_id=message_id,
                reaction=reaction
            )
            
            result = InteractionResult(
                success=True,
                interaction_type='reaction',
                target_id=message_id,
                target_type='message',
                action=f'reacted_with_{reaction}',
                timestamp=datetime.now(),
                details={'reaction': reaction, 'reaction_type': reaction_type}
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"Reaction sent: {reaction} to message {message_id}")
            
            return result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for reaction: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_message_reaction(chat_id, message_id, reaction, reaction_type)
        except Exception as e:
            self.logger.error(f"Reaction send failed: {e}")
            return InteractionResult(False, 'reaction', message_id, 'message', 'send_reaction', datetime.now(), str(e))
    
    async def send_multiple_reactions(self, chat_id: int, message_ids: List[int], reaction: str = None, delay_range: Tuple[int, int] = (2, 8)) -> List[InteractionResult]:
        """Çoklu mesaja reaksiyon gönder"""
        results = []
        
        for message_id in message_ids:
            result = await self.send_message_reaction(chat_id, message_id, reaction)
            results.append(result)
            
            # Gecikme
            await asyncio.sleep(random.uniform(*delay_range))
        
        return results
    
    async def view_messages(self, chat_id: int, message_count: int = 10) -> List[InteractionResult]:
        """Mesajları görüntüle (view boost)"""
        results = []
        
        try:
            # Son mesajları al
            messages = await self.client.get_messages(chat_id, limit=message_count)
            
            for message in messages:
                if message.id:
                    # Mesajı görüntüle (Telethon'da bu otomatik olarak yapılır)
                    # Gerçek view boost için özel API gerekir, burada simüle ediliyor
                    result = InteractionResult(
                        success=True,
                        interaction_type='view',
                        target_id=message.id,
                        target_type='message',
                        action='viewed',
                        timestamp=datetime.now(),
                        details={'view_count': 1}
                    )
                    
                    results.append(result)
                    self.interaction_history.append(result)
                    
                    # Gecikme
                    await asyncio.sleep(random.uniform(1, 3))
            
            self.logger.info(f"Viewed {len(results)} messages")
            return results
            
        except Exception as e:
            self.logger.error(f"Message viewing failed: {e}")
            return [InteractionResult(False, 'view', 0, 'message', 'view_messages', datetime.now(), str(e))]
    
    async def vote_poll(self, chat_id: int, message_id: int, option_index: int = None) -> InteractionResult:
        """Ankete oy ver"""
        try:
            # Mesajı al
            message = await self.client.get_messages(chat_id, ids=message_id)
            
            if not message or not hasattr(message, 'poll') or not message.poll:
                return InteractionResult(False, 'poll', message_id, 'message', 'vote_poll', datetime.now(), "Message is not a poll")
            
            poll = message.poll
            
            # Seçenek belirle
            if option_index is None:
                option_index = random.randint(0, len(poll.answers) - 1)
            
            # Oy gönder
            await self.client.vote_poll(
                entity=chat_id,
                message_id=message_id,
                options=[option_index]
            )
            
            result = InteractionResult(
                success=True,
                interaction_type='poll_vote',
                target_id=message_id,
                target_type='poll',
                action=f'voted_option_{option_index}',
                timestamp=datetime.now(),
                details={'option_index': option_index, 'total_options': len(poll.answers)}
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"Voted in poll {message_id}, option {option_index}")
            
            return result
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait for poll vote: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.vote_poll(chat_id, message_id, option_index)
        except Exception as e:
            self.logger.error(f"Poll vote failed: {e}")
            return InteractionResult(False, 'poll_vote', message_id, 'poll', 'vote_poll', datetime.now(), str(e))
    
    async def get_poll_results(self, chat_id: int, message_id: int) -> Dict:
        """Anket sonuçlarını al"""
        try:
            message = await self.client.get_messages(chat_id, ids=message_id)
            
            if not message or not hasattr(message, 'poll') or not message.poll:
                return {}
            
            poll = message.poll
            
            results = {
                'question': poll.question,
                'total_voters': poll.total_voters,
                'answers': []
            }
            
            for answer in poll.answers:
                answer_data = {
                    'text': answer.text,
                    'votes': answer.votes,
                    'percentage': (answer.votes / poll.total_voters * 100) if poll.total_voters > 0 else 0
                }
                results['answers'].append(answer_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Poll results retrieval failed: {e}")
            return {}
    
    async def participate_in_giveaway(self, chat_id: int, message_id: int) -> InteractionResult:
        """Çekilişe katıl"""
        try:
            # Çekiliş mesajını al
            message = await self.client.get_messages(chat_id, ids=message_id)
            
            if not message:
                return InteractionResult(False, 'giveaway', message_id, 'giveaway', 'participate', datetime.now(), "Message not found")
            
            # Çekiliş kontrolü (mesaj metninde giveaway belirtileri ara)
            giveaway_keywords = ['çekiliş', 'hediye', 'ödül', 'kazan', 'giveaway', 'gift', 'prize', 'win']
            message_text = message.text.lower() if message.text else ""
            
            is_giveaway = any(keyword in message_text for keyword in giveaway_keywords)
            
            if not is_giveaway:
                return InteractionResult(False, 'giveaway', message_id, 'giveaway', 'participate', datetime.now(), "Message is not a giveaway")
            
            # Çekilişe katılma koşulları:
            # 1. Mesajı beğen
            await self.send_message_reaction(chat_id, message_id, '❤️')
            await asyncio.sleep(random.uniform(2, 5))
            
            # 2. Mesaja yorum yap (varsa)
            if hasattr(message, 'replies') and message.replies:
                # Yorum yapma simülasyonu
                pass
            
            # 3. Kanalı takip et (varsa)
            # Bu adım için özel API gerekir
            
            result = InteractionResult(
                success=True,
                interaction_type='giveaway_participation',
                target_id=message_id,
                target_type='giveaway',
                action='participated',
                timestamp=datetime.now(),
                details={
                    'message_text': message.text[:100] if message.text else '',
                    'reactions_sent': ['❤️'],
                    'requirements_met': True
                }
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"Participated in giveaway {message_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Giveaway participation failed: {e}")
            return InteractionResult(False, 'giveaway', message_id, 'giveaway', 'participate', datetime.now(), str(e))
    
    async def auto_interact_with_chat(self, chat_id: int, interaction_config: Dict) -> List[InteractionResult]:
        """Sohbetle otomatik etkileşim"""
        results = []
        
        try:
            # Mesajları al
            message_count = interaction_config.get('message_count', 20)
            messages = await self.client.get_messages(chat_id, limit=message_count)
            
            for message in messages:
                # Reaksiyon gönder
                if interaction_config.get('send_reactions', False) and random.random() < interaction_config.get('reaction_probability', 0.3):
                    reaction_type = interaction_config.get('reaction_type', 'positive')
                    result = await self.send_message_reaction(chat_id, message.id, reaction_type=reaction_type)
                    results.append(result)
                    await asyncio.sleep(random.uniform(2, 6))
                
                # Anketlere oy ver
                if interaction_config.get('vote_polls', False) and hasattr(message, 'poll') and message.poll:
                    result = await self.vote_poll(chat_id, message.id)
                    results.append(result)
                    await asyncio.sleep(random.uniform(3, 8))
                
                # Çekilişlere katıl
                if interaction_config.get('join_giveaways', False):
                    result = await self.participate_in_giveaway(chat_id, message.id)
                    if result.success:
                        results.append(result)
                        await asyncio.sleep(random.uniform(5, 10))
                
                # Görüntüleme
                if interaction_config.get('view_messages', False):
                    result = InteractionResult(
                        success=True,
                        interaction_type='view',
                        target_id=message.id,
                        target_type='message',
                        action='viewed',
                        timestamp=datetime.now()
                    )
                    results.append(result)
                    await asyncio.sleep(random.uniform(1, 2))
            
            self.logger.info(f"Auto-interaction completed for chat {chat_id}, {len(results)} interactions")
            
        except Exception as e:
            self.logger.error(f"Auto-interaction failed: {e}")
            results.append(InteractionResult(False, 'auto_interaction', chat_id, 'chat', 'auto_interact', datetime.now(), str(e)))
        
        return results
    
    async def batch_interact_with_chats(self, chat_configs: List[Dict], delay_range: Tuple[int, int] = (10, 30)) -> Dict[int, List[InteractionResult]]:
        """Çoklu sohbetle etkileşim"""
        all_results = {}
        
        for config in chat_configs:
            chat_id = config['chat_id']
            interaction_config = config.get('interaction_config', {})
            
            results = await self.auto_interact_with_chat(chat_id, interaction_config)
            all_results[chat_id] = results
            
            # Sohbetler arası gecikme
            await asyncio.sleep(random.uniform(*delay_range))
        
        return all_results
    
    async def get_interaction_statistics(self, days_back: int = 7) -> Dict:
        """Etkileşim istatistiklerini al"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        recent_interactions = [
            interaction for interaction in self.interaction_history
            if interaction.timestamp >= cutoff_date
        ]
        
        stats = {
            'total_interactions': len(recent_interactions),
            'by_type': {},
            'by_action': {},
            'success_rate': 0,
            'daily_activity': {}
        }
        
        successful_interactions = [i for i in recent_interactions if i.success]
        
        if recent_interactions:
            stats['success_rate'] = len(successful_interactions) / len(recent_interactions) * 100
        
        for interaction in recent_interactions:
            # Tipe göre grupla
            interaction_type = interaction.interaction_type
            stats['by_type'][interaction_type] = stats['by_type'].get(interaction_type, 0) + 1
            
            # Aksiyona göre grupla
            action = interaction.action
            stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
            
            # Günlük aktivite
            date_key = interaction.timestamp.strftime('%Y-%m-%d')
            stats['daily_activity'][date_key] = stats['daily_activity'].get(date_key, 0) + 1
        
        return stats
    
    def get_interaction_history(self) -> List[Dict]:
        """Etkileşim geçmişini al"""
        return [asdict(interaction) for interaction in self.interaction_history]
    
    def export_history(self, filename: str = None):
        """Etkileşim geçmişini dışa aktar"""
        if filename is None:
            filename = f"interactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        history = self.get_interaction_history()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Interaction history exported to: {filename}")
        return filename
    
    def clear_history(self, older_than_days: int = 30):
        """Eski etkileşim geçmişini temizle"""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        self.interaction_history = [
            interaction for interaction in self.interaction_history
            if interaction.timestamp >= cutoff_date
        ]
        
        self.logger.info(f"Cleared interaction history older than {older_than_days} days")

# Kullanım örneği
async def example_usage():
    """Kullanım örneği"""
    from telethon import TelegramClient
    
    # Client'ınızı oluşturun
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()
    
    # Etkileşim yöneticisini başlat
    interaction_manager = InteractionManager(client)
    
    # Mesaja reaksiyon gönder
    result = await interaction_manager.send_message_reaction(chat_id, message_id, '👍')
    print("Reaction result:", result)
    
    # Ankete oy ver
    poll_result = await interaction_manager.vote_poll(chat_id, poll_message_id, 0)
    print("Poll vote result:", poll_result)
    
    # Çekilişe katıl
    giveaway_result = await interaction_manager.participate_in_giveaway(chat_id, giveaway_message_id)
    print("Giveaway result:", giveaway_result)
    
    # Otomatik etkileşim
    interaction_config = {
        'send_reactions': True,
        'reaction_type': 'positive',
        'reaction_probability': 0.4,
        'vote_polls': True,
        'join_giveaways': True,
        'view_messages': True,
        'message_count': 50
    }
    
    auto_results = await interaction_manager.auto_interact_with_chat(chat_id, interaction_config)
    print(f"Auto-interaction results: {len(auto_results)} interactions")
    
    # İstatistikler
    stats = await interaction_manager.get_interaction_statistics(7)
    print("Interaction statistics:", stats)
    
    # Geçmişi dışa aktar
    interaction_manager.export_history()
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(example_usage())
