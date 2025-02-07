import asyncio
from aiogram import Bot, Dispatcher
from handlers_new import router
from middlewares import LoggingMiddleware

# bot = Bot(token=TOKEN)
bot = Bot(token="7433278727:AAF01LEDHtXm8lscAZ9WkhStKPEafQmuFSE")
dp = Dispatcher()
dp.include_router(router)
dp.message.middleware(LoggingMiddleware())


async def main():
   print("Бот запущен!")
   await dp.start_polling(bot)


if __name__ == "__main__":
   asyncio.run(main())