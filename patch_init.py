import re

with open('master_bot/handlers/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from master_bot.handlers.promocode import router as promocode_router' not in content:
    content = content.replace('from master_bot.handlers.referral import router as referral_router', 'from master_bot.handlers.referral import router as referral_router\nfrom master_bot.handlers.promocode import router as promocode_router')
    
if 'promocode_router' not in content.split('router.include_router')[1:]:
    content = content.replace('router.include_router(referral_router)', 'router.include_router(referral_router)\n    router.include_router(promocode_router)')

with open('master_bot/handlers/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)
