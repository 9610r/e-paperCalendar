# -*- coding: utf-8 -*-
import calendar as cal
from datetime import date, datetime
import itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import logging
from lib import epd7in5_V2
from connect_calendar import Calendar

OpenWeatherToken = "<YOUR OpenWeather API AccessToken>"

def get_calendar(year: int, month: int):
    calendar_eu = cal.monthcalendar(year, month)
    formatted = [0]+list(itertools.chain.from_iterable(calendar_eu))[:-1]
    return np.array(formatted).reshape(-1, 7).tolist()


def get_font(font_symbol: str, font_size: int):
    return ImageFont.truetype(font_files[font_symbol], font_size)


def get_width(text: str, font_symbol: str, font_size: int):
    bbox = draw.multiline_textbbox(
        (0, 0), text,
        font=get_font(font_symbol, font_size)
    )
    return bbox[2] - bbox[0]


def padding_width(width: int, text: str, font_symbol: str, font_size: int):
    return (width - get_width(text, font_symbol, font_size)) // 2

def today_weather():
    import requests

    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    headers= {}
    params={
        "appid": OpenWeatherToken,
        "id" : "1863289",
        "units": "metric",
        # "lang":"ja"
    }
    result = requests.get(endpoint, headers=headers, params=params)

    return result

logging.basicConfig(level=logging.DEBUG)

epd = epd7in5_V2.EPD()

logging.info('init and Clear')
epd.init()
epd.Clear()

font_files = dict(
    ja='./Fonts/NotoSansJP-Regular.otf',
    num='./Fonts/Cardo-Regular.ttf',
    cale='./Fonts/TenorSans-Regular.ttf',
    tempFont='./Fonts/Anton-Regular.ttf',
    title='./Fonts/BebasNeue-Regular.ttf'
)

# color scale
COLOR = dict(
    black=(0, 0, 0),
#    red=(256, 0, 0),
    white=(255, 255, 255)
)
# image size
SIZE = (800, 480)
MAIN_WIDTH = 480
# create a new image
img = Image.new('RGB', SIZE, COLOR['white'])

today = date.today()
year = today.year
month = today.month
days = today.day
# get my schedule and holidays
events, event_days, holidays = Calendar.get_events(today)

draw = ImageDraw.Draw(img)

# show year
draw.multiline_text(
    (10, 10), str(year), fill=COLOR['black'], font=get_font('cale', 30)
)

draw.multiline_text((padding_width(MAIN_WIDTH , str(month), 'title', 70), 10), str(month),
    fill=COLOR['black'], font=get_font('title', 70)
)
# draw.line(((10, 100), (MAIN_WIDTH - 10, 100)),fill=COLOR['black'], width=2)


# labels of weekday
weekday = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
weekday_s = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

# this month
# get the calendar of this month
calendar = get_calendar(year, month)

w_day = MAIN_WIDTH // 7
x_start = np.arange(7) * w_day

# show the label of weekday
for i, text in enumerate(weekday):
    w_pad = padding_width(w_day, text, 'cale', 25)
    color = COLOR['black']
    draw.multiline_text((x_start[i] + w_pad, 100),
                        text, font=get_font('cale', 25), fill=color)

draw.line(((10, 130), (MAIN_WIDTH - 10, 130)), fill=COLOR['black'], width=3)

# show the dates
difference_h = 0
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            if i == 6:
                difference_h = 1
            continue

        w_pad = padding_width(w_day, str(text), 'cale', 30)

        if text == days:
            draw.ellipse((x_start[i] + (w_day - 40) // 2, 150 + 52 * (h - difference_h), x_start[i] + (w_day - 40) // 2 + 43, 150 + 52 * (h - difference_h) + 43 ),fill=(0, 0, 0))
            color = COLOR['white']
            draw.multiline_text((x_start[i] + w_pad, 150 + 52 * (h - difference_h)),
                                str(text), font=get_font('cale', 35), fill=color)
        else:
            color = COLOR['black']
            draw.multiline_text((x_start[i] + w_pad, 150 + 52 * (h - difference_h)),
                                str(text), font=get_font('cale', 35), fill=color)
        if text in event_days:
            draw.line(((x_start[i] + (w_day - 12) // 2, 193 + 52 * (h - difference_h)),
                       (x_start[i] + (w_day - 12) // 2 + 15, 193 + 52 * (h - difference_h))), fill=COLOR['black'])


# a boundary between calendar and schedule
draw.line(
    ((MAIN_WIDTH, 0), (MAIN_WIDTH, SIZE[1])),
    fill=COLOR['black'],
    width=1
)
draw.line(
    ((MAIN_WIDTH + 2, 0), (MAIN_WIDTH + 2, SIZE[1])),
    fill=COLOR['black'],
    width=1
)

# show the schedule
event_count = 8
draw.line(((MAIN_WIDTH + 16, 6 + 200, (SIZE[0] - 16, 6 + 200))),
            fill=COLOR['black'])
for h, event in enumerate(events[:event_count]):
    dt = "/".join([str(int(i)) for i in event[1][0].split("-")[1:]])
    text = f'{dt + "  " * ( 5 - len(dt))}' \
        + f'{f" {event[1][1][:5]}" if len(event[1]) != 1 else ""}' \
        + f' {event[0] if len(event[0]) < 20 else event[0][:10] + "…"}'
    draw.multiline_text((MAIN_WIDTH + 10,  (6 + 30 * h) + 200),
                        text, font=get_font('ja', 18), fill=COLOR['black'])
    if 0 < h < 8:
        draw.line(
            ((MAIN_WIDTH + 16, (6 + 30 * h) + 200, (SIZE[0] - 16,  (6 + 30 * h) + 200))),
            fill=COLOR['black'],
            width=1
        )

dt = datetime.now().isoformat(sep=' ')[:16].replace('-', '.')
draw.multiline_text((550, SIZE[1] - 30), f'Updated at {dt}',
                    font=get_font('ja', 16), fill=COLOR['black'])

result = today_weather()
data = result.json()
temp = data["main"]["temp"]
humidity = data["main"]["humidity"]
image_str = data["weather"][0]["icon"]

icon_dict = {
    "humid": "wi-humidity.jpeg",
    "temp": "wi-thermometer.jpeg",
    "01d": "wi-day-sunny.jpeg",
    "02d": "wi-day-cloudy.jpeg",
    "03d": "wi-cloudy.jpeg",
    "04d": "wi-cloudy-windy.jpeg",
    "09d": "wi-showers.jpeg",
    "10d": "wi-rain.jpeg",
    "11d": "wi-thunderstorm.jpeg",
    "13d": "wi-snow.jpeg",
    "50d": "wi-fog.jpeg",
    "Na" : "wi-na.jpeg"
}
tenki_image_name = None

if image_str in icon_dict:
    tenki_image_name = icon_dict[image_str]
else:
    tenki_image_name = icon_dict["Na"]

# 天気アイコン貼り付け
tenki_image = Image.open(f'./weather-icons/{tenki_image_name}')
temp_image = Image.open(f'./weather-icons/{icon_dict["temp"]}')
humid_image = Image.open(f'./weather-icons/{icon_dict["humid"]}')

img.paste(tenki_image, (490, 0))
img.paste(temp_image, (620, 10))
img.paste(humid_image, (620, 90))
# 気温
draw.multiline_text((660, 40), str(temp), font=get_font('tempFont', 40), fill=COLOR['black'])
draw.multiline_text((get_width(str(temp), 'tempFont', 40) + 660 + 5, 50),
                    '℃', font=get_font('ja', 30), fill=COLOR['black'])
# 湿度
draw.multiline_text((660, 120), str(humidity), font=get_font('tempFont', 40), fill=COLOR['black'])
draw.multiline_text((get_width(str(humidity), 'tempFont', 50) + 660 + 5, 130),
                    '％', font=get_font('ja', 30), fill=COLOR['black'])


# show the calendar on e-paper
epd.display(epd.getbuffer(img))
epd.sleep()

# save an image for test
img.save('image.bmp', 'bmp')
