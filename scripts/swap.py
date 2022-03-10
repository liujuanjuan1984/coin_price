import requests
import json
from officepy import JsonFile
import datetime

# assets id in mixin network.
USDT = "4d8c508b-91c5-375b-92b0-ee702ed2dac5"
RUM = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"
XIN = "c94ac88f-4671-3976-b60a-09064f1811e8"
BTC = "c6d0c728-2624-429b-8e0d-d9d19b6592fa"
ETH = "43d61dcd-e413-450d-80b8-101d5e903357"
EOS = "6cfe566e-4aad-470b-8c9a-2fd35b49c68d"
BOX = "f5ef6b5d-cc5a-3d90-b2c0-a2fd386e7a3c"


class SwapPrice:
    def __init__(self):
        headers = {"Accepts": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.baseurl = "https://api.4swap.org/api"

    def _price(self, quote, base, amount_id=None):
        api = self.baseurl + f"/pairs/{quote}/{base}"
        data = self.session.get(api).json()["data"]
        price = round(float(data["base_amount"]) / float(data["quote_amount"]), 2)
        if price < 1:
            price = round(float(data["quote_amount"]) / float(data["base_amount"]), 2)
        if data["base_asset_id"] == amount_id:
            amount = float(data["base_amount"])
        elif data["quote_asset_id"] == amount_id:
            amount = float(data["quote_amount"])
        else:
            amount = None
        return price, amount

    def rum(self):
        rum_usdt, a1 = self._price(RUM, USDT, RUM)
        xin_rum, a2 = self._price(RUM, XIN, RUM)
        btc_usdt, _ = self._price(BTC, USDT)
        eth_usdt, _ = self._price(ETH, USDT)
        xin_usdt, _ = self._price(XIN, USDT)
        box_usdt, _ = self._price(BOX, USDT)
        eos_usdt, _ = self._price(EOS, USDT)

        a = f"""=== RUM 流动池 ===\n【{round(a1+a2,2)}】小计 \n【{round(a1,2)}】RUM/USDT 汇率 {rum_usdt}\n【{round(a2,2)}】XIN/RUM 汇率 {xin_rum}\n{str(datetime.datetime.now())[:19]}"""

        b = f"""=== RUM 汇率 ===\nBTC/RUM 汇率 {round(btc_usdt/rum_usdt,2)}\nETH/RUM 汇率 {round(eth_usdt/rum_usdt,2)}\nBOX/RUM 汇率 {round(box_usdt/rum_usdt,2)}\nEOS/RUM 汇率 {round(eos_usdt/rum_usdt,2)}"""

        return a, b
