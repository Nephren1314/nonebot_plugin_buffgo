import requests
import re
import html
import json
from pathlib import Path
from nonebot import get_bot, get_driver
from selenium import webdriver
from nonebot import on_command
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')

@scheduler.scheduled_job("cron", minute="*/5", id="job_0")
async def run():
    module_path: Path = Path(__file__).parent
    keyword_path: Path = module_path / "resource/data.json"
    temp_path : Path = module_path / "resource/temp.txt"
    data: dict = json.load(open(keyword_path, "r", encoding="utf-8"))
    keys = data.keys()
    result = ''
    result0 = ''
    price = []
    driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
    for key in keys:
        driver.get(f'https://buff.163.com/goods/{key}')
        html_str = driver.page_source
        text = html.unescape(html_str)
        pattern = r'(\S+)\s+¥\s+(\d+)'
        numbers = str(re.findall(pattern, text))
        price += [int(n) for n in re.findall(r'\d+', numbers)]
        result += f'{data[key]}' + ':' + numbers + '|'
    with open(f'{temp_path}', 'r+') as output:
        state = False
        out = ''.join(output.readlines())
        old_price = [int(n) for n in re.findall(r'\d+', out)]
        if len(old_price) == 0:
            pass
        else:
            for i in range(0, len(price)):
                if price[i] < old_price[i]*0.97 and price[i] > old_price[i]*1.02:
                    pattern1 = r'([^|]*{}[^|]*)\|'.format(price[i])
                    pattern2 = r'([^|]*{}[^|]*)\|'.format(old_price[i])
                    result0 = "原价"+str(re.findall(pattern2, out))+'\n'+"现价"+str(re.findall(pattern1, result))
                    state = True
        output.seek(0)
        output.truncate(0)
        output.write(result)
    await sendtosuperuser(result0, state)
    driver.quit()

async def sendtosuperuser(result0 : str, state: bool):
    superusers = get_driver().config.superusers
    bot = get_bot()
    message = result0
    if state:
        for superuser in superusers:
            await bot.call_api(
                "send_msg",
                **{
                    "message": message,
                    "user_id": superuser,
                },
            )
