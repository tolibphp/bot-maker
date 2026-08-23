from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_ref_bonus = State()
    waiting_min_withdraw = State()
    waiting_channel_username = State()
    waiting_payout_channel = State()

class UserStates(StatesGroup):
    waiting_withdraw_details = State()
