from aiogram.filters import BaseFilter
from aiogram.types import Message
from functions import get_food_data


class WeightFilter(BaseFilter):
   async def __call__(self, message: Message) -> bool:
       if 10 <= float(message.text) <= 600:
           return True
       else:
           await message.answer(
               text="Некорректный вес.\nДиапазон для веса — от 10 до 600 кг."
           )
           return False
  
class HeightFilter(BaseFilter):
   async def __call__(self, message: Message,) -> bool:
       if 50 <= float(message.text) <= 300:
           return True
       else:
           await message.answer(
               text="Некорректный рост.\nДиапазон для роста — от 50 до 300 см."
           )
           return False


class AgeFilter(BaseFilter):
   async def __call__(self, message: Message) -> bool:
       if 12 <= float(message.text) <= 130:
           return True
       else:
           await message.answer(
               text="Некорректный возраст.\nДиапазон для возраста — от 12 до 130 лет."
           )
           return False
      
class ActivityFilter(BaseFilter):
   async def __call__(self, message: Message) -> bool:
       if 0 <= float(message.text) <= 720:
           return True
       else:
           await message.answer(
               text="Некорректное время активности.\nАктивность должна длится не более 720 мин."
           )
           return False

class LoggingFoodFilter:
    def __init__(self, message, command):
        self.message = message
        self.command = command
    
    async def validate_command(self):
        if self.command.args is None:
            await self.message.answer(
                "Не передан аргумент.\nВ качестве аргумента передайте название продукта, например: /log_food banana"
            )
            return False
        return True
    
    async def validate_food_data(self, input_food):
        try:
            data_food, _status = await get_food_data(input_food)
            return data_food
        except:
            await self.message.answer(
                "Такого продукта не существует или продукт введен неверно.\nВведите название продукта, например: /log_food banana"
            )
            return None

class LoggingWaterFilter:
    def __init__(self, message, command):
        self.message = message
        self.command = command

    async def validate_command(self):
        if self.command.args is None:
            await self.message.answer(
                "Не передан аргумент.\nВ качестве аргумента передайте количество выпитой воды в мл, например: /log_water 200"
            )
            return False
        return True
    
    async def validate_input(self, input_water):
        try:
            return float(input_water)
        except ValueError:
            await self.message.answer(
                "Некорректно введен аргумент.\nВ качестве аргумента передайте количество выпитой воды в мл, например: /log_water 200"
            )
            return None
        
class LoggingTrainsFilter:
    def __init__(self, message, command):
        self.message = message
        self.command = command

    async def validate_command(self):
        if self.command.args is None:
            await self.message.answer(
                "Не переданы аргументы.\nВ качестве аргументов передайте тип тренировки и время тренировки в минутах, например: /log_workout бег 30"
            )
            return False
        return True

    async def parse_args(self):
        try:
            workout_type, workout_time = self.command.args.split(" ", maxsplit=1)
            workout_time = float(workout_time)
            return workout_type, workout_time
        except ValueError:
            await self.message.answer(
                "Некорректно введены аргументы.\nВ качестве аргументов передайте тип тренировки и время тренировки в минутах, например: /log_workout бег 30"
            )
            return None, None