from aiogram.fsm.state import State, StatesGroup


class CreateBotStates(StatesGroup):
    choosing_template = State()
    waiting_token = State()
    confirming = State()


class AdminAddBalanceStates(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()


class AdminBroadcastStates(StatesGroup):
    waiting_message = State()


class AdminPriceStates(StatesGroup):
    waiting_price_type = State()
    waiting_new_price = State()
