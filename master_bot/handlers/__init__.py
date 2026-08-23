from aiogram import Router
from master_bot.handlers.start import router as start_router
from master_bot.handlers.create_bot import router as create_bot_router
from master_bot.handlers.my_bots import router as my_bots_router
from master_bot.handlers.balance import router as balance_router
from master_bot.handlers.referral import router as referral_router
from master_bot.handlers.admin import router as admin_router


def get_master_router() -> Router:
    master_router = Router()
    master_router.include_router(start_router)
    master_router.include_router(create_bot_router)
    master_router.include_router(my_bots_router)
    master_router.include_router(balance_router)
    master_router.include_router(referral_router)
    master_router.include_router(admin_router)
    return master_router
