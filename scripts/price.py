import requests
from datetime import timedelta, datetime
import json
from time import sleep
from config import CMC_PRO_API_KEY  # coinmarketcap 的密钥


def _origin_data(n=2):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    parameters = {"start": "1", "limit": str(n), "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_PRO_API_KEY}

    for i in range(n):  # 如不成功，就持续尝试 3 次，每次间隔 10 分钟
        try:
            session = requests.Session()
            session.headers.update(headers)
            data = session.get(url, params=parameters).json()
            return data
        except Exception as e:
            print(e)
            sleep(5 * 60)


def prices(data=None, n=2):

    if data == None:
        print(datetime.now(), "price is none.try it again.")
        data = _origin_data(n)

    if data == None:
        return {}

    info = {}
    for i in range(0, n):
        symbol = data["data"][i]["symbol"]
        usd = round(float(data["data"][i]["quote"]["USD"]["price"]), 2)
        price_24h = round(
            float(data["data"][i]["quote"]["USD"]["percent_change_24h"]), 2
        )
        price_30d = round(
            float(data["data"][i]["quote"]["USD"]["percent_change_30d"]), 2
        )
        timetemp = data["data"][0]["last_updated"]
        beijing = str(
            datetime.strptime(timetemp[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=8)
        )
        itext = f"""==={symbol}===\nUSD {usd}\n24H {price_24h}%\n30D {price_30d}%\n{beijing}"""
        info[symbol] = {
            "USD": usd,
            "price_24h": price_24h,
            "price_30d": price_30d,
            "time": beijing,
            "text": itext,
        }
    return info


if __name__ == "__main__":
    info = prices(n=2)
    print(info)
