from aiogram.fsm.state import State, StatesGroup


class AddMovieStates(StatesGroup):
    waiting_name = State()
    waiting_category = State()
    waiting_file = State()


class AddCategoryStates(StatesGroup):
    waiting_name = State()


class AddChannelStates(StatesGroup):
    waiting_channel = State()


class BroadcastStates(StatesGroup):
    waiting_message = State()


class BanUserStates(StatesGroup):
    waiting_user_id = State()


class DeleteMovieStates(StatesGroup):
    waiting_code = State()


class SearchStates(StatesGroup):
    waiting_query = State()
