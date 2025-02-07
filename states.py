from aiogram.fsm.state import State, StatesGroup

class ProfileUser(StatesGroup):
   weight = State()
   height = State()
   age = State()
   activity = State()
   city = State()
   calories_obj = State()


class LoggingFood(StatesGroup):
   log_eat_water_trains = State()