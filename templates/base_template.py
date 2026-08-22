from abc import ABC, abstractmethod
from aiogram import Bot, Dispatcher


class BaseTemplate(ABC):
    def __init__(self, bot_token: str, admin_id: int, db_path: str, bot_id: int):
        self.bot_token = bot_token
        self.admin_id = admin_id
        self.db_path = db_path
        self.bot_id = bot_id
        self.bot: Bot = None
        self.dp: Dispatcher = None

    @abstractmethod
    async def setup(self):
        """Setup bot dispatcher and handlers."""
        pass

    @abstractmethod
    async def start(self):
        """Start polling."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop polling."""
        pass
