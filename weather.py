from bs4 import BeautifulSoup
import requests
import json

from config import TEN_DAYS_URL, HOURS_URL


def get_ten_days_weather():
    source = requests.get(TEN_DAYS_URL).text
    soup = BeautifulSoup(source, 'lxml')

    # 获取所有卡片的html代码
    days = soup.find_all('details', attrs={"data-testid": "ExpandedDetailsCard"})[1:]
    weather_data = []
    weather_summary = {}
    day_weather = {}
    night_weather = {}
    for day in days:
        # 获取日期：周二 04
        date = day.find_all('h2', attrs={'data-testid': "daypartName"})
        weather_summary['date'] = date[0].text

        # 温度信息： 32°/25°
        temperature = day.find_all('span', attrs={'data-testid': "TemperatureValue"})
        weather_summary['temperature'] = f"{temperature[0].text}/{temperature[1].text}"
        day_weather['temperature'] = temperature[0].text
        night_weather['temperature'] = temperature[1].text

        # 天气概况：雷暴。 最高 29ºC。 南 风 10 到 15 每 km / h
        weather_status = day.find_all('div', attrs={'data-testid': "wxIcon"})
        weather_summary['weather_status'] = weather_status[0].text

        # 下雨的概率和湿度
        rain_and_humidity = day.find_all('span', attrs={'data-testid': "PercentageValue"})
        weather_summary['rain_probability'] = rain_and_humidity[0].text
        day_weather['rain_probability'] = rain_and_humidity[1].text
        day_weather['humidity'] = rain_and_humidity[2].text
        night_weather['rain_probability'] = rain_and_humidity[3].text
        night_weather['humidity'] = rain_and_humidity[4].text

        # 风：西北偏西 9 公里/小时
        winds = day.find_all('span', attrs={'data-testid': "Wind"})
        weather_summary['wind'], day_weather['wind'], night_weather['wind'] = [wind.text for wind in winds]

        # 白天和晚上的天气概况：雷暴。 最低 23ºC。 西北偏西 风，风向多变。 降雨几率 80%。
        wx_phrases = day.find_all('p', attrs={'data-testid': "wxPhrase"})
        day_weather['weather_status'], night_weather['weather_status'] = [wx_phrase.text for wx_phrase in wx_phrases]

        # 紫外线指数
        ultraviolet = day.find_all('span', attrs={'data-testid': "UVIndexValue"})
        day_weather['ultraviolet'], night_weather['ultraviolet'] = [x.text for x in ultraviolet]

        # 日出日落，月升月落
        sun_rise = day.find_all('span', attrs={'data-testid': "SunriseTime"})[0].text
        sun_set = day.find_all('span', attrs={'data-testid': "SunsetTime"})[0].text
        moon_rise = day.find_all('span', attrs={'data-testid': "MoonriseTime"})[0].text
        moon_set = day.find_all('span', attrs={'data-testid': "MoonsetTime"})[0].text
        day_weather['sun_rise'] = sun_rise
        day_weather['sun_set'] = sun_set
        night_weather['moon_rise'] = moon_rise
        night_weather['moon_set'] = moon_set
        weather_data.append([weather_summary, day_weather, night_weather])
        # ------------------单个卡片获取完毕，循环获取下一个卡片信息----------------------

    # 将所有信息写入一个txt文档中
    with open('./weather_data/ten_days.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(weather_data, ensure_ascii=False))


def get_hours_weather():
    try:
        source = requests.get(HOURS_URL).text
    except Exception as e:
        print(e)
        print('an error occurred when make a requests: hour weather')
        return 'error'
    soup = BeautifulSoup(source, 'lxml')

    # 获取各个小时的天气信息的的html代码
    details = soup.find_all('details', attrs={'data-testid': 'ExpandedDetailsCard'})
    hours_weather = []
    for detail in details:
        # 获取当前时间：10:00
        hour = detail.find_all('h2', attrs={"data-testid": "daypartName"})[0].text

        # 获取温度信息：23°
        temperature = detail.find_all('span', attrs={'data-testid': 'TemperatureValue'})[0].text

        # 天气概况：大部分地区多云
        weather_summary = detail.find_all('div', attrs={'data-testid': 'wxIcon'})[0].text

        # 降雨概率和湿度信息
        rain = detail.find_all('span', attrs={'data-testid': 'PercentageValue'})

        # 风力
        wind = detail.find_all('span', attrs={'data-testid': 'Wind'})[0].text

        # 紫外线指数
        ultraviolet = detail.find_all('span', attrs={"data-testid": "UVIndexValue"})[0].text
        hour_weather = {
            "time": hour,
            "temperature": temperature,
            "summary": weather_summary,
            "rain": rain[0].text,
            "humidity": rain[1].text,
            "wind": wind,
            "ultraviolet": ultraviolet
        }
        hours_weather.append(hour_weather)
        # ------------------单个卡片获取完毕，循环获取下一个卡片信息----------------------

    # 将所有信息写入一个txt文档中
    with open('./weather_data/hours.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(hours_weather, ensure_ascii=False))


if __name__ == "__main__":
    get_ten_days_weather()
    get_hours_weather()
