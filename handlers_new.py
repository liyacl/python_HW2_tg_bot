import asyncio
from aiogram import F, Router
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from filters import WeightFilter, HeightFilter, AgeFilter, ActivityFilter, LoggingFoodFilter, LoggingWaterFilter, LoggingTrainsFilter
from states import ProfileUser
from functions import calc_calories, calc_water, calc_burned_calories, calc_drinked_water
from states import LoggingFood

router = Router()


### 1. /start ###
@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
   await state.clear()
   await message.answer(
       "Привет! Я бот для расчёта нормы воды, калорий и трекинга активности.\n"
       "Чтобы ознакомиться со всеми доступными командами, введите /help.\n"
   )


### 2. /help ###
@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
   await message.answer(
       "Доступные команды:\n"
       "/start - Начать работу\n"
       "/help - Помощь\n"
       "/set_profile - Настройка профиля пользователя\n"
       "/log_water <количество воды> - Логирование воды\n"
       "/log_food <название продукта> - Логирование еды\n"
       "/log_workout <тип тренировки> <время (мин)> - Логирование тренировок\n"
       "/check_progress - Показать прогресс по воде и калориям"
   )
   

### 3. /set_profile + add weight ###
@router.message(StateFilter(None), Command("set_profile"))
# @router.message(StateFilter(None), Command("set_profile"))
async def add_weight(message: Message, state: FSMContext):
   await message.answer(text="Введите ваш вес (в кг):")
   # устанавливаем состояние
   await state.set_state(ProfileUser.weight)


### 4. add height ###
@router.message(ProfileUser.weight, WeightFilter())
async def add_height(message: Message, state: FSMContext):
   # сохраняем состояние
   await state.update_data(weight=float(message.text))
   await message.answer(text="Введите ваш рост (в см):")
   await state.set_state(ProfileUser.height)


### 5. add age ###
@router.message(ProfileUser.height, HeightFilter())
async def add_age(message: Message, state: FSMContext):
   await state.update_data(height=float(message.text))
   await message.answer(text="Введите ваш возраст:")
   await state.set_state(ProfileUser.age)



### 6. add activity ###
@router.message(ProfileUser.age, AgeFilter())
async def add_activity(message: Message, state: FSMContext):
   await state.update_data(age=float(message.text))
   await message.answer(text="Сколько минут активности у вас в день?")
   await state.set_state(ProfileUser.activity)


### 7. add city ###
@router.message(ProfileUser.activity, ActivityFilter())
async def add_city(message: Message, state: FSMContext):
   await state.update_data(activity=float(message.text))
   await message.answer(text="В каком городе вы находитесь?")
   await state.set_state(ProfileUser.city)


### 8. add calories objective ###
@router.message(ProfileUser.city)
async def add_calories_obj(message: Message, state: FSMContext):
   await state.update_data(city=message.text.lower().title())
   await message.answer(text="Какая у вас цель по потреблению калорий (в сутки)?")
   await state.set_state(ProfileUser.calories_obj)


### 9. calculate the norms of water and calories ###
@router.message(ProfileUser.calories_obj)
async def calculate_norms(message: Message, state: FSMContext):
   await state.update_data(calories_obj=float(message.text))
   # получаем все переменные
   data = await state.get_data()
   calories = await calc_calories(data["weight"], data["height"], data["age"], data["activity"])
   water = await calc_water(data["weight"], data["activity"], data["city"])

   await message.answer(
       text=f"Суточная норма воды: {water} мл. \nСуточная норма каллорий: {calories} ккал."
   )
   await state.update_data(water_goal=water)
   await state.update_data(calorie_goal=calories)

   # очищаем состояние
   await state.set_state(state=None)


### 10. add log water ###
@router.message(Command("log_water"))
async def add_log_water(message: Message, command: CommandObject, state: FSMContext):
    logger = LoggingWaterFilter(message, command)
    if not await logger.validate_command():
        return

    water = command.args
    valid_input = await logger.validate_input(water)
    if valid_input is None:
        return

    if not (await state.get_data()).get("logged_water", None):
        await state.update_data(logged_water=valid_input)
    else:
        _water_now = (await state.get_data())["logged_water"]
        await state.update_data(logged_water=_water_now + valid_input)

    await message.answer(f"До выполнения нормы осталось {(await state.get_data())['water_goal'] - (await state.get_data())['logged_water']} мл.")


### 11. add log food ###
@router.message(StateFilter(None), Command("log_food"))
async def add_log_food(message: Message, command: CommandObject, state: FSMContext):
    logger = LoggingFoodFilter(message, command)

    if not await logger.validate_command():
        return

    food = command.args
    data_food = await logger.validate_food_data(food)

    if data_food is not None:
        await message.answer(
            f"{food.title()} — {data_food['foods'][0]['nf_calories']} ккал на {data_food['foods'][0]['serving_weight_grams']} г. Сколько грамм вы съели?"
        )
        await state.update_data(food_name=food)
        await state.update_data(food_calories=float(data_food["foods"][0]["nf_calories"]))
        await state.update_data(food_grams=float(data_food["foods"][0]["serving_weight_grams"]))
        await state.set_state(LoggingFood.log_eat_water_trains)


### 12. add calculating food calories ###
@router.message(LoggingFood.log_eat_water_trains)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(log_eat_water_trains=float(message.text))

    data = await state.get_data()
    logged_calories = (data["food_calories"] / data["food_grams"]) * data["log_eat_water_trains"]
    if not (await state.get_data()).get("logged_calories", None):
        await state.update_data(logged_calories=float(logged_calories))
    else:
        _calories_now = (await state.get_data())["logged_calories"]
        # записываем всю историю калорий
        await state.update_data(logged_calories=_calories_now + float(logged_calories))
    await message.answer(f"Записано: {logged_calories} ккал.")
    await state.set_state(state=None)


### 13. add logging workout ###
@router.message(Command("log_workout"))
async def add_log_trains(message: Message, command: CommandObject, state: FSMContext):
    logger = LoggingTrainsFilter(message, command)
    if not await logger.validate_command():
        return

    workout_type, workout_time = await logger.parse_args()
    if workout_type is None or workout_time is None:
        return

    burned_calories = calc_burned_calories(workout_type, workout_time)
    drinked_water = calc_drinked_water(workout_type, workout_time)

    if not (await state.get_data()).get("burned_calories", None):
        await state.update_data(burned_calories=float(burned_calories))
    else:
        _trains_now = (await state.get_data())["burned_calories"]
        await state.update_data(burned_calories=_trains_now + float(burned_calories))

    if not (await state.get_data()).get("water_goal", None):
        await message.answer(
            "Вы не указали объём выпитой воды.\nЧтобы заполнить профиль, введите команду /set_profile"
        )
    else:
        _trains_now = (await state.get_data())["water_goal"]
        await state.update_data(water_goal=_trains_now + float(drinked_water))

    await message.answer(
        f"{workout_type.lower().title()} {workout_time} минут — {burned_calories} ккал. Дополнительно: выпейте {drinked_water} мл воды."
    )
    
### 14. add progress ###
@router.message(Command("check_progress"))
async def check_progress(message: Message, command: CommandObject, state: FSMContext):
    data = await state.get_data()
    
    if not all([data.get("water_goal"), data.get("calorie_goal")]):
        return await message.answer(
            "Отсутствуют сведения по ежедневным нормам воды и калорий. \nЗаполните, пожалуйста свой профиль, введя команду /set_profile"
        )

    data.setdefault("logged_water", 0)
    data.setdefault("logged_calories", 0)
    data.setdefault("burned_calories", 0)

    progress_message = (
        f"""
        Прогресс:
        Вода:
        - Выпито: {data["logged_water"]} мл. из {data["water_goal"]}
        - Осталось: {data["water_goal"] - data["logged_water"]} мл.
        
        Калории:
        - Потреблено: {data["logged_calories"]} ккал. из {data["calorie_goal"]}
        - Сожжено: {data["burned_calories"]} ккал.
        - Баланс: {data["logged_calories"] - data["burned_calories"]} ккал."""
    )
    
    return await message.answer(progress_message)
