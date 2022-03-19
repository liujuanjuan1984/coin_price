import requests
from datetime import timedelta, datetime
from config import CMC_PRO_API_KEY  # coinmarketcap 的密钥


class CoinmarketcapPrice:
    def __init__(self, n=2):
        self.n = n

    def _origin_data(self):
        headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_PRO_API_KEY}
        session = requests.Session()
        session.headers.update(headers)
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        parameters = {"start": "1", "limit": str(self.n), "convert": "USD"}
        try:
            resp = session.get(url, params=parameters).json()
            return resp
        except Exception as e:
            print(e)

    def _info_data(self, data):
        info = {}
        for i in range(0, self.n):
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
                datetime.strptime(timetemp[:19], "%Y-%m-%dT%H:%M:%S")
                + timedelta(hours=8)
            )
            itext = f"""==={symbol}===\nUSD {usd}\n24H {price_24h}%\n30D {price_30d}%\n{beijing}"""
            info[symbol] = {
                "USD": usd,
                "price_24h": price_24h,
                "price_30d": price_30d,
                "time": beijing,
                "text": [itext],
            }
        return info

    def price(self, data=None):
        data = data or self._origin_data()
        if data:
            return self._info_data(data)
        return {}


if __name__ == "__main__":
    info = CoinmarketcapPrice().price()
    print(info)
