import asyncio
from datetime import datetime
from config import TEMPLATES
from bot_manager import manager
from database.bots import get_bots_needing_payment, update_bot_status, extend_bot_free_until
from database.users import get_balance, update_balance
from database.payments import add_payment

async def daily_subscription_check(bot):
    while True:
        try:
            print("[CRON] Checking subscriptions...")
            bots_needing_payment = await get_bots_needing_payment()
            
            for b in bots_needing_payment:
                bot_id = b['id']
                owner_id = b['owner_telegram_id']
                template = TEMPLATES.get(b['template_type'])
                
                if not template:
                    continue
                    
                daily_price = template.get('daily_price', 2000)
                balance = await get_balance(owner_id)
                
                if balance >= daily_price:
                    # Deduct money and extend
                    await update_balance(owner_id, -daily_price)
                    await extend_bot_free_until(bot_id, 1)
                    
                    await add_payment(
                        user_telegram_id=owner_id,
                        amount=-daily_price,
                        payment_type="daily_fee",
                        description=f"Kunlik to'lov: @{b['bot_username']}"
                    )
                    
                    try:
                        await bot.send_message(
                            owner_id,
                            f"? <b>Kunlik to'lov yechildi!</b>\n\n"
                            f"?? Bot: @{b['bot_username']}\n"
                            f"?? Miqdor: <b>{daily_price:,} so'm</b>\n\n"
                            f"Botingiz muvaffaqiyatli yana 1 kunga uzaytirildi.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                else:
                    # Not enough balance, stop the bot
                    await update_bot_status(bot_id, 'inactive')
                    await manager.stop_bot(bot_id)
                    
                    try:
                        await bot.send_message(
                            owner_id,
                            f"?? <b>Botingiz to'xtatildi!</b>\n\n"
                            f"?? Bot: @{b['bot_username']}\n"
                            f"Kunlik to'lov ({daily_price:,} so'm) uchun balansingizda mablag' yetarli emas.\n\n"
                            f"Iltimos, balansingizni to'ldiring va botni qayta ishga tushiring.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"[CRON] Error: {e}")
            
        # Check every 1 hour (3600 seconds)
        await asyncio.sleep(3600)
