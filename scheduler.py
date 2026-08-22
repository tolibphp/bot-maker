import asyncio
import logging
from datetime import datetime

from database.bots import get_bots_needing_payment, update_bot_status, update_last_payment, get_bot
from database.users import get_balance, update_balance
from database.payments import add_payment
from config import DAILY_FEE

logger = logging.getLogger(__name__)


async def check_daily_payments():
    """Check all bots and process daily payments for expired free trials."""
    logger.info("Running daily payment check...")

    bots = await get_bots_needing_payment()
    logger.info(f"Found {len(bots)} bots needing payment check")

    for bot_data in bots:
        bot_id = bot_data["id"]
        owner_id = bot_data["owner_telegram_id"]

        # Check owner's balance
        balance = await get_balance(owner_id)

        if balance >= DAILY_FEE:
            # Deduct daily fee
            await update_balance(owner_id, -DAILY_FEE)
            await add_payment(
                user_telegram_id=owner_id,
                amount=-DAILY_FEE,
                payment_type="daily_fee",
                description=f"Kunlik to'lov: @{bot_data['bot_username']}"
            )
            await update_last_payment(bot_id)
            logger.info(
                f"Daily fee collected for bot #{bot_id} "
                f"(@{bot_data['bot_username']}) from user {owner_id}"
            )

            # Notify owner
            try:
                from aiogram import Bot as AioBot
                # We need the master bot to send notification
                from config import MASTER_TOKEN
                notify_bot = AioBot(token=MASTER_TOKEN)
                await notify_bot.send_message(
                    owner_id,
                    f"💰 <b>Kunlik to'lov</b>\n\n"
                    f"🤖 @{bot_data['bot_username']} uchun\n"
                    f"💸 {DAILY_FEE:,} so'm yechildi\n"
                    f"💰 Qoldiq: {balance - DAILY_FEE:,} so'm",
                    parse_mode="HTML"
                )
                await notify_bot.session.close()
            except Exception:
                pass

        else:
            # Not enough balance — stop the bot
            from bot_manager import manager
            await manager.stop_bot(bot_id)
            await update_bot_status(bot_id, "expired")

            logger.warning(
                f"Bot #{bot_id} (@{bot_data['bot_username']}) stopped — "
                f"insufficient balance for user {owner_id}"
            )

            # Notify owner
            try:
                from aiogram import Bot as AioBot
                from config import MASTER_TOKEN
                notify_bot = AioBot(token=MASTER_TOKEN)
                await notify_bot.send_message(
                    owner_id,
                    f"⛔ <b>Bot to'xtatildi!</b>\n\n"
                    f"🤖 @{bot_data['bot_username']}\n"
                    f"💰 Balans yetarli emas ({balance:,} so'm)\n"
                    f"💲 Kerakli summa: {DAILY_FEE:,} so'm/kun\n\n"
                    f"💳 Balansni to'ldirib, botni qayta ishga tushiring.",
                    parse_mode="HTML"
                )
                await notify_bot.session.close()
            except Exception:
                pass


async def run_scheduler():
    """Run the payment scheduler — checks every hour."""
    logger.info("Scheduler started — checking payments every hour")

    while True:
        try:
            await check_daily_payments()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        # Wait 1 hour before next check
        await asyncio.sleep(3600)
