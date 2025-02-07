import warnings
warnings.filterwarnings('ignore')
import aiohttp

WEATHER_API = "1c37661d92f5c05d4a9758b52c3d9e30"
FOOD_API_ID="efd30dca"
FOOD_API_KEY="5dddb96e08298605579dc7df072801ee"
      
async def get_weather_info(city, api_key=WEATHER_API):
   url = "http://api.openweathermap.org/data/2.5/weather"
   params = {"q": city, "appid": api_key, "units": "metric"}
   async with aiohttp.ClientSession() as session:
       async with session.get(url, params=params) as response:
           return await response.json(), response.status

async def get_food_data(product_name,
                        api_id=FOOD_API_ID,
                        api_key=FOOD_API_KEY):
   url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
   async with aiohttp.ClientSession() as session:
       async with session.post(url,
                               headers={"x-app-id": f"{api_id}",
                                        "x-app-key": f"{api_key}"},
                                        json={"query": f"{product_name}"}) as response:
           return await response.json(), response.status

async def calc_water(weight: float, activity: float, city:str):
   temp, _ = await get_weather_info(city=city.lower().title())
   print(weight, activity, city, temp['main']['temp'])
   if temp['main']['temp'] > 25:
       return 30 * weight + 500 * (activity // 30) + 500
   else:
       return 30 * weight + 500 * (activity // 30)
  
async def calc_calories(weight: float, height: float, age: float, activity: float):
   if activity <= 15:
       return 10 * weight + 6.25 * height - 5 * age
   elif activity <= 60:
       return 10 * weight + 6.25 * height - 5 * age + 200
   else:
       return 10 * weight + 6.25 * height - 5 * age + 400
   
def calc_burned_calories(workout_type, workout_time):
    return (
        100 * workout_time // 10
        if workout_type.lower() == "бег"
        else 50 * workout_time // 10
    )
    
def calc_drinked_water(workout_type, workout_time):
    return (
        150 * workout_time // 10
        if workout_type.lower() == "бег"
        else 100 * workout_time // 10
    )