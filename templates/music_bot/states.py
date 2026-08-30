from aiogram.fsm.state import State, StatesGroup

class BroadcastStates(StatesGroup):
    waiting_message = State()

class AddChannelStates(StatesGroup):
    waiting_channel = State()
