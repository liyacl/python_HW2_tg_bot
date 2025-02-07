import asyncio
from aiogram import Bot, Dispatcher
from handlers_new import router
from middlewares import LoggingMiddleware
from config import BOT_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)
dp.message.middleware(LoggingMiddleware())


async def main():
   print("Бот запущен!")
   await dp.start_polling(bot)


if __name__ == "__main__":
   asyncio.run(main())
