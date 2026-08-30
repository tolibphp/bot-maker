from aiogram.fsm.state import State, StatesGroup


class CreateBotStates(StatesGroup):
    choosing_template = State()
    waiting_token = State()
    confirming = State()


class PaymentStates(StatesGroup):
    waiting_amount = State()
    waiting_screenshot = State()


class AdminAddBalanceStates(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()


class AddChannelStates(StatesGroup):
    waiting_channel = State()


class AdminBroadcastStates(StatesGroup):
    waiting_message = State()


class AdminPriceStates(StatesGroup):
    waiting_price_type = State()
    waiting_new_price = State()

class PromocodeStates(StatesGroup):
    waiting_code = State()
    waiting_reward = State()
    waiting_limit = State()

class UsePromocodeStates(StatesGroup):
    waiting_code = State()
