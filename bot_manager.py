import asyncio
import logging

from database.bots import get_all_active_bots, get_bot, update_bot_status
from templates.base_template import BaseTemplate
from templates.kino_bot import KinoBot
from templates.stars_bot import StarsBot
from templates.money_bot import MoneyBot

logger = logging.getLogger(__name__)


class BotManager:
    def __init__(self):
        self._running_bots: dict[int, BaseTemplate] = {}  # bot_id -> Bot instance

    async def start_bot(self, bot_id: int):
        """Start a bot by its database ID."""
        if bot_id in self._running_bots:
            logger.warning(f"Bot #{bot_id} is already running")
            return

        bot_data = await get_bot(bot_id)
        if not bot_data:
            raise ValueError(f"Bot #{bot_id} not found in database")

        try:
            if bot_data["template_type"] == "kino":
                bot_instance = KinoBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )
            elif bot_data["template_type"] == "stars":
                bot_instance = StarsBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )
            elif bot_data["template_type"] == "money":
                bot_instance = MoneyBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )
            elif bot_data["template_type"] == "downloader":
                from templates.downloader_bot import DownloaderBot
                bot_instance = DownloaderBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )
            elif bot_data["template_type"] == "music":
                from templates.music_bot import MusicBot
                bot_instance = MusicBot(
                    bot_token=bot_data["bot_token"],
                    admin_id=bot_data["owner_telegram_id"],
                    db_path=bot_data["db_path"],
                    bot_id=bot_id
                )
            else:
                raise ValueError(f"Unknown template type: {bot_data['template_type']}")

            await bot_instance.start()
            self._running_bots[bot_id] = bot_instance
            await update_bot_status(bot_id, "active")
            logger.info(f"Bot #{bot_id} (@{bot_data['bot_username']}) started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot #{bot_id}: {e}")
            raise

    async def stop_bot(self, bot_id: int):
        """Stop a running bot."""
        bot_instance = self._running_bots.get(bot_id)
        if bot_instance:
            try:
                await bot_instance.stop()
            except Exception as e:
                logger.error(f"Error stopping bot #{bot_id}: {e}")
            finally:
                del self._running_bots[bot_id]
            logger.info(f"Bot #{bot_id} stopped")
        else:
            logger.warning(f"Bot #{bot_id} is not running")

    async def restart_bot(self, bot_id: int):
        """Restart a bot."""
        await self.stop_bot(bot_id)
        await asyncio.sleep(1)
        await self.start_bot(bot_id)

    async def load_all_bots(self):
        """Load and start all active bots from database."""
        active_bots = await get_all_active_bots()
        logger.info(f"Loading {len(active_bots)} active bots...")

        for bot_data in active_bots:
            try:
                await self.start_bot(bot_data["id"])
                await asyncio.sleep(0.5)  # Small delay between starts
            except Exception as e:
                logger.error(
                    f"Failed to load bot #{bot_data['id']} "
                    f"(@{bot_data['bot_username']}): {e}"
                )

        logger.info(
            f"Loaded {len(self._running_bots)}/{len(active_bots)} bots successfully"
        )

    async def stop_all_bots(self):
        """Stop all running bots."""
        bot_ids = list(self._running_bots.keys())
        for bot_id in bot_ids:
            await self.stop_bot(bot_id)
        logger.info("All bots stopped")

    def is_running(self, bot_id: int) -> bool:
        """Check if a bot is currently running."""
        return bot_id in self._running_bots

    def get_running_count(self) -> int:
        """Get number of currently running bots."""
        return len(self._running_bots)

    def get_running_bot_ids(self) -> list[int]:
        """Get list of running bot IDs."""
        return list(self._running_bots.keys())


# Global manager instance
manager = BotManager()
