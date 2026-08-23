from datetime import datetime
import aiosqlite
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from templates.stars_bot.database import StarsDB
from templates.stars_bot.keyboards import admin_main_kb, settings_kb, channels_manage_kb, cancel_kb, main_menu_kb, post_bot_link_kb
from templates.stars_bot.states import AdminStates

def create_admin_router(stars_db: StarsDB, admin_id: int) -> Router:
    router = Router()

    @router.message(Command("admin"))
    async def cmd_admin(message: Message, state: FSMContext):
        if message.from_user.id != admin_id:
            return
        await state.clear()
        await message.answer("👑 <b>Admin Panel</b>", reply_markup=admin_main_kb(), parse_mode="HTML")

    @router.message(F.text == "⚙️ Sozlamalar")
    async def show_settings(message: Message):
        if message.from_user.id != admin_id:
            return
        ref_bonus = await stars_db.get_setting("ref_bonus")
        min_withdraw = await stars_db.get_setting("min_withdraw")
        
        await message.answer(
            f"⚙️ <b>Sozlamalar</b>\n\n"
            f"Referal narxi: <b>{ref_bonus} ⭐️</b>\n"
            f"Minimal yechish: <b>{min_withdraw} ⭐️</b>",
            reply_markup=settings_kb(ref_bonus, min_withdraw),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "set_ref_bonus")
    async def set_ref_bonus(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Yangi referal bonusini kiriting (faqat raqam):",
            reply_markup=cancel_kb()
        )
        await state.set_state(AdminStates.waiting_ref_bonus)

    @router.message(AdminStates.waiting_ref_bonus)
    async def save_ref_bonus(message: Message, state: FSMContext):
        try:
            val = int(message.text)
        except ValueError:
            await message.answer("Faqat raqam kiriting!")
            return
        await stars_db.set_setting("ref_bonus", str(val))
        await message.answer(f"✅ Referal bonus <b>{val} ⭐️</b> qilib belgilandi.", parse_mode="HTML")
        await state.clear()
        await show_settings(message)

    @router.callback_query(F.data == "set_min_withdraw")
    async def set_min_withdraw(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Yangi minimal yechish miqdorini kiriting (faqat raqam):",
            reply_markup=cancel_kb()
        )
        await state.set_state(AdminStates.waiting_min_withdraw)

    @router.message(AdminStates.waiting_min_withdraw)
    async def save_min_withdraw(message: Message, state: FSMContext):
        try:
            val = int(message.text)
        except ValueError:
            await message.answer("Faqat raqam kiriting!")
            return
        await stars_db.set_setting("min_withdraw", str(val))
        await message.answer(f"✅ Minimal yechish <b>{val} ⭐️</b> qilib belgilandi.", parse_mode="HTML")
        await state.clear()
        await show_settings(message)

    @router.message(F.text == "✅ Majburiy obuna")
    async def show_channels(message: Message):
        if message.from_user.id != admin_id:
            return
        channels = await stars_db.get_channels()
        await message.answer(
            "📢 <b>Majburiy kanallar ro'yxati:</b>",
            reply_markup=channels_manage_kb(channels),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "add_channel")
    async def add_channel(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Kanal usernamesini yuboring (masalan: @kanalim):\n\n"
            "<i>Eslatma: Bot kanalda admin bo'lishi shart!</i>",
            reply_markup=cancel_kb(),
            parse_mode="HTML"
        )
        await state.set_state(AdminStates.waiting_channel_username)

    @router.message(AdminStates.waiting_channel_username)
    async def save_channel(message: Message, state: FSMContext):
        username = message.text
        if not username.startswith("@"):
            username = "@" + username
            
        try:
            chat = await message.bot.get_chat(username)
            await stars_db.add_channel(chat.id, username)
            await message.answer(f"✅ Kanal qo'shildi: {username}")
        except Exception as e:
            await message.answer(f"❌ Xatolik. Bot kanalda admin emasmi yoki username noto'g'rimi?\n\n{e}")
            
        await state.clear()
        await show_channels(message)

    @router.callback_query(F.data.startswith("delch:"))
    async def del_channel(callback: CallbackQuery):
        ch_id = int(callback.data.split(":")[1])
        await stars_db.delete_channel(ch_id)
        await callback.answer("✅ Kanal o'chirildi", show_alert=True)
        # Refresh
        channels = await stars_db.get_channels()
        await callback.message.edit_reply_markup(reply_markup=channels_manage_kb(channels))

    @router.message(F.text == "📢 To'lovlar kanali")
    async def set_payout_channel(message: Message, state: FSMContext):
        if message.from_user.id != admin_id:
            return
        curr = await stars_db.get_setting("payout_channel_username")
        await message.answer(
            f"Joriy to'lovlar kanali: {curr or 'Yoq'}\n\n"
            f"Yangi to'lovlar kanali usernamesini yuboring (masalan: @tolovlar):\n"
            f"<i>Bot kanalda admin bo'lishi shart, u yerga to'lov cheklarini yuboradi.</i>",
            reply_markup=cancel_kb(),
            parse_mode="HTML"
        )
        await state.set_state(AdminStates.waiting_payout_channel)

    @router.message(AdminStates.waiting_payout_channel)
    async def save_payout_channel(message: Message, state: FSMContext):
        username = message.text
        if not username.startswith("@"):
            username = "@" + username
        
        try:
            chat = await message.bot.get_chat(username)
            await stars_db.set_setting("payout_channel_id", str(chat.id))
            await stars_db.set_setting("payout_channel_username", username)
            await message.answer(f"✅ To'lovlar kanali saqlandi: {username}")
        except Exception as e:
            await message.answer(f"❌ Xatolik. Bot u kanalda admin emas!\n{e}")
        await state.clear()

    @router.message(F.text == "📈 Statistika")
    async def show_stats(message: Message):
        if message.from_user.id != admin_id:
            return
        users_count = await stars_db.get_users_count()
        await message.answer(
            f"📈 <b>Statistika</b>\n\n"
            f"👥 Umumiy foydalanuvchilar: <b>{users_count}</b> ta",
            parse_mode="HTML"
        )

    @router.message(F.text == "🖼 Referral rasm")
    async def set_ref_photo(message: Message, state: FSMContext):
        if message.from_user.id != admin_id:
            return
        await message.answer(
            "🖼 Yangi referral rasmini yuboring:\n\n"
            "<i>Bekor qilish uchun /cancel bosing.</i>",
            reply_markup=cancel_kb()
        )
        await state.set_state(AdminStates.waiting_ref_photo)

    @router.message(AdminStates.waiting_ref_photo, F.photo)
    async def save_ref_photo(message: Message, state: FSMContext):
        photo_id = message.photo[-1].file_id
        await stars_db.set_setting("ref_photo_id", photo_id)
        await message.answer("✅ Referral rasmi muvaffaqiyatli saqlandi!")
        await state.clear()

    @router.message(F.text == "📢 Broadcast")
    async def broadcast_start(message: Message, state: FSMContext):
        if message.from_user.id != admin_id:
            return
        await message.answer(
            "Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
            "<i>(Xabar, rasm, video yoki istalgan fayl yuborishingiz mumkin)</i>",
            reply_markup=cancel_kb()
        )
        await state.set_state(AdminStates.waiting_broadcast_message)

    @router.message(AdminStates.waiting_broadcast_message)
    async def broadcast_send(message: Message, state: FSMContext):
        import asyncio
        from templates.stars_bot.database import StarsDB
        
        await state.clear()
        
        # Get all users (we need a way to get all users in database.py, but for now we can just select all)
        # We don't have get_all_users() in stars_db, so I'll write a quick raw query here
        async with aiosqlite.connect(stars_db.db_path) as db:
            cursor = await db.execute("SELECT telegram_id FROM users")
            users = await cursor.fetchall()
        
        if not users:
            await message.answer("Foydalanuvchilar topilmadi.")
            return
            
        await message.answer(f"📢 Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")
        
        success = 0
        failed = 0
        
        for user in users:
            try:
                await message.copy_to(chat_id=user[0])
                success += 1
                await asyncio.sleep(0.05) # Prevent flood wait
            except Exception:
                failed += 1
                
        await message.answer(f"✅ <b>Broadcast yakunlandi!</b>\n\n🟢 Yuborildi: {success}\n🔴 Yuborilmadi: {failed}", parse_mode="HTML")

    @router.callback_query(F.data == "close_admin")
    async def close_admin_inline(callback: CallbackQuery):
        await callback.message.delete()

    @router.callback_query(F.data == "cancel_admin")
    async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi.")

    # --- Payout Approval Logic ---
    @router.callback_query(F.data.startswith("payout_approve:"))
    async def approve_payout(callback: CallbackQuery):
        _, user_id_str, amount_str = callback.data.split(":")
        user_id = int(user_id_str)
        amount = int(amount_str)

        # Update button to show it's done
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>To'lab berildi!</b>", parse_mode="HTML")

        # Notify user
        try:
            await callback.bot.send_message(
                user_id,
                f"✅ <b>To'lovingiz amalga oshirildi!</b>\n\n"
                f"Sizning <b>{amount} ⭐️</b> lik so'rovingiz tasdiqlandi. "
                f"Pul yoki Yulduzchalar hisobingizga tushirildi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Post to payout channel
        payout_ch_id = await stars_db.get_setting("payout_channel_id")
        if payout_ch_id:
            bot_me = await callback.bot.get_me()
            now = datetime.now().strftime("%d-%B, %H:%M")
            user = await stars_db.get_user(user_id)
            
            # Since we only have user_id in callback, we might not have the full username. 
            # We can use the user_id as a link.
            post_text = (
                f"🎉 <b>Yangi to'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={user_id}'>Foydalanuvchi</a>\n"
                f"💰 Yechib olindi: <b>{amount} ⭐️</b>\n"
                f"📅 Sana: {now}\n\n"
                f"👇 Siz ham Stars ishlashni boshlang!"
            )
            try:
                await callback.bot.send_message(
                    int(payout_ch_id),
                    post_text,
                    reply_markup=post_bot_link_kb(bot_me.username),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    @router.callback_query(F.data.startswith("payout_reject:"))
    async def reject_payout(callback: CallbackQuery):
        _, user_id_str, amount_str = callback.data.split(":")
        user_id = int(user_id_str)
        amount = int(amount_str)

        await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>Rad etildi!</b>", parse_mode="HTML")

        # Refund
        await stars_db.update_balance(user_id, amount)

        try:
            await callback.bot.send_message(
                user_id,
                f"❌ <b>To'lov rad etildi.</b>\n\n"
                f"<b>{amount} ⭐️</b> balansingizga qaytarildi. Iltimos, ma'lumotlarni to'g'ri kiritib qayta urinib ko'ring.",
                parse_mode="HTML"
            )
        except Exception:
            pass

    return router
