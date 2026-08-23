from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.stars_bot.database import StarsDB
from templates.stars_bot.keyboards import main_menu_kb, admin_main_kb
from templates.stars_bot.handlers.subscription import check_subscription, send_subscription_message
from templates.stars_bot.states import UserStates

def create_user_router(stars_db: StarsDB, admin_id: int) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        user_id = message.from_user.id
        text = message.text or ""

        # Check sub
        if not await check_subscription(message.bot, user_id, stars_db):
            await send_subscription_message(message, stars_db)
            return

        # Referral logic
        referrer_id = None
        if " " in text:
            arg = text.split(" ", 1)[1].strip()
            if arg.startswith("ref_"):
                try:
                    referrer_id = int(arg[4:])
                    if referrer_id == user_id:
                        referrer_id = None
                except ValueError:
                    pass

        is_new = await stars_db.add_user(user_id, referred_by=referrer_id)
        
        if is_new and referrer_id:
            # Reward referrer
            ref_bonus = int(await stars_db.get_setting("ref_bonus"))
            await stars_db.update_balance(referrer_id, ref_bonus)
            try:
                await message.bot.send_message(
                    referrer_id,
                    f"🎉 <b>Yangi referal!</b>\n\n"
                    f"👤 {message.from_user.full_name} sizning havolangiz orqali qo'shildi.\n"
                    f"💰 <b>+{ref_bonus} ⭐️</b> balansga qo'shildi!",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        await message.answer(
            f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            f"⭐️ <b>Stars ishlash botiga xush kelibsiz!</b>\n\n"
            f"Do'stlaringizni taklif qiling va <b>Telegram Stars</b> (yoki pul) ishlang!",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "check_sub")
    async def check_sub_callback(callback: CallbackQuery):
        if not await check_subscription(callback.bot, callback.from_user.id, stars_db):
            await callback.answer("Hali hamma kanallarga obuna bo'lmapsiz!", show_alert=True)
            return
        
        await callback.message.delete()
        await callback.message.answer(
            f"✅ <b>Obuna tasdiqlandi!</b>\n\n"
            f"Endi botdan to'liq foydalanishingiz mumkin.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )

    @router.message(F.text == "💰 Balansim")
    async def show_balance(message: Message):
        if not await check_subscription(message.bot, message.from_user.id, stars_db):
            await send_subscription_message(message, stars_db)
            return

        user_id = message.from_user.id
        user = await stars_db.get_user(user_id)
        
        await message.answer(
            f"💰 <b>Sizning balansingiz</b>\n\n"
            f"💵 Joriy balans: <b>{user['balance']} ⭐️</b>\n"
            f"📈 Jami ishlangan: <b>{user.get('total_earned', 0)} ⭐️</b>",
            parse_mode="HTML"
        )

    @router.message(F.text == "⭐️ Stars ishlash")
    async def earn_stars(message: Message):
        if not await check_subscription(message.bot, message.from_user.id, stars_db):
            await send_subscription_message(message, stars_db)
            return

        user_id = message.from_user.id
        bot_me = await message.bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start=ref_{user_id}"
        
        ref_count = await stars_db.get_referral_count(user_id)
        ref_bonus = int(await stars_db.get_setting("ref_bonus"))
        user = await stars_db.get_user(user_id)
        ref_photo = await stars_db.get_setting("ref_photo_id")

        from templates.stars_bot.keyboards import share_ref_link_kb

        text = (
            f"🔗 <b>Do'stlarni taklif qiling!</b>\n\n"
            f"Har bir taklif qilingan do'stingiz uchun <b>{ref_bonus} ⭐️</b> olasiz!\n\n"
            f"📊 <b>Sizning statistika:</b>\n"
            f"👥 Takliflar: <b>{ref_count}</b> ta\n"
            f"💰 Balans: <b>{user['balance']} ⭐️</b>\n\n"
            f"👇 <b>Sizning taklif havolangiz:</b>\n"
            f"<code>{ref_link}</code>\n\n"
            f"Buni nusxalab do'stlaringizga yuboring!"
        )

        if ref_photo:
            await message.answer_photo(
                photo=ref_photo,
                caption=text,
                reply_markup=share_ref_link_kb(ref_link),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text,
                reply_markup=share_ref_link_kb(ref_link),
                parse_mode="HTML"
            )

    @router.message(F.text == "💸 Stars yechish")
    async def withdraw_stars(message: Message, state: FSMContext):
        if not await check_subscription(message.bot, message.from_user.id, stars_db):
            await send_subscription_message(message, stars_db)
            return

        user_id = message.from_user.id
        user = await stars_db.get_user(user_id)
        min_withdraw = int(await stars_db.get_setting("min_withdraw"))

        if user['balance'] < min_withdraw:
            await message.answer(
                f"❌ <b>Balans yetarli emas!</b>\n\n"
                f"Sizning balans: <b>{user['balance']} ⭐️</b>\n"
                f"Minimal yechish: <b>{min_withdraw} ⭐️</b>\n\n"
                f"Yana do'stlaringizni taklif qiling!",
                parse_mode="HTML"
            )
            return

        await state.update_data(withdraw_amount=user['balance'])
        await message.answer(
            f"💸 <b>Pul (Stars) yechish</b>\n\n"
            f"Sizning balans: <b>{user['balance']} ⭐️</b>\n\n"
            f"Iltimos, yulduzchalarni qabul qilib oluvchi <b>Username</b> yoki <b>Karta raqamingizni</b> yozib yuboring:",
            parse_mode="HTML"
        )
        await state.set_state(UserStates.waiting_withdraw_details)

    @router.message(UserStates.waiting_withdraw_details)
    async def withdraw_details(message: Message, state: FSMContext):
        details = message.text
        data = await state.get_data()
        amount = data['withdraw_amount']
        user_id = message.from_user.id
        user = message.from_user

        # Remove stars from user balance
        await stars_db.update_balance(user_id, -amount)

        # Notify admin
        from templates.stars_bot.keyboards import payout_approve_kb
        admin_text = (
            f"💸 <b>Yangi pul yechish so'rovi!</b>\n\n"
            f"👤 User: {user.full_name}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"💰 Miqdor: <b>{amount} ⭐️</b>\n\n"
            f"📝 Qabul qiluvchi (Rekvizit): \n<code>{details}</code>\n\n"
            f"To'lovni amalga oshirgach 'To'landi' tugmasini bosing."
        )
        try:
            await message.bot.send_message(
                admin_id,
                admin_text,
                reply_markup=payout_approve_kb(user_id, amount),
                parse_mode="HTML"
            )
        except Exception:
            pass

        await message.answer(
            f"✅ <b>So'rov adminga yuborildi!</b>\n\n"
            f"Miqdor: <b>{amount} ⭐️</b>\n"
            f"To'lov tasdiqlangach sizga xabar beramiz.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        await state.clear()

    @router.message(F.text == "📊 To'lovlar")
    async def show_payouts(message: Message):
        payout_channel = await stars_db.get_setting("payout_channel_username")
        if payout_channel:
            await message.answer(
                f"📊 Bizning barcha to'lovlarimiz shu kanalda e'lon qilib boriladi:\n\n"
                f"👉 {payout_channel}"
            )
        else:
            await message.answer("📊 To'lovlar kanali hali sozlanmagan.")

    @router.message(F.text == "ℹ️ FAQ")
    async def show_faq(message: Message):
        ref_bonus = await stars_db.get_setting("ref_bonus")
        min_withdraw = await stars_db.get_setting("min_withdraw")
        
        await message.answer(
            f"ℹ️ <b>Qanday qilib ishlash kerak?</b>\n\n"
            f"1. <b>⭐️ Stars ishlash</b> tugmasini bosing va o'z havolangizni oling.\n"
            f"2. Havolani do'stlaringizga yuboring.\n"
            f"3. Har bir qo'shilgan do'stingiz uchun <b>{ref_bonus} ⭐️</b> olasiz.\n"
            f"4. Balansingiz <b>{min_withdraw} ⭐️</b> ga yetganda uni yechib olishingiz mumkin.\n\n"
            f"Do'stlaringiz bot kanallariga obuna bo'lishi shart, aks holda bonus berilmaydi!",
            parse_mode="HTML"
        )

    # Allow admin to switch back to admin menu if they act like a user
    @router.message(F.text == "👤 User rejimi")
    async def user_mode(message: Message):
        if message.from_user.id == admin_id:
            await message.answer("👤 User rejimidasiz. Admin panelga qaytish uchun /admin bosing.", reply_markup=main_menu_kb())

    return router
