import requests
import json
import os
import datetime
from officepy import JsonFile, Dir

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
Dir(data_dir).check()
assetsfile = os.path.join(this_dir, "data", "assets.json")
pairsfile = os.path.join(this_dir, "data", "pairs.json")


class SwapPrice:
    """
    4swap (base on mixin network) mtg price bot
    https://github.com/fox-one/4swap-sdk-go/blob/master/docs/api.md
    """

    def __init__(self):
        headers = {"Accepts": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.baseurl = "https://api.4swap.org/api"

    def pairs(self):
        if os.path.exists(pairsfile):
            origin_data = JsonFile(pairsfile).read()
        else:
            origin_data = self.session.get(f"{self.baseurl}/pairs").json()
            JsonFile(pairsfile).write(origin_data)
        origin_data = origin_data["data"]["pairs"]

        return [(item["base_asset_id"], item["quote_asset_id"]) for item in origin_data]

    def paris_symbol(self, symbol):
        return [item for item in self.pairs() if self.get_id(symbol) in item]

    def pair(self, base_asset_id, quote_asset_id):
        api = f"{self.baseurl}/pairs/{base_asset_id}/{quote_asset_id}"
        try:
            data = self.session.get(api).json()["data"]
            return data
        except Exception as e:
            print(e)
            return {}

    def assets(self):
        if os.path.exists(assetsfile):
            origin_data = JsonFile(assetsfile).read()
        else:
            origin_data = self.session.get(f"{self.baseurl}/pairs").json()
            JsonFile(assetsfile).write(origin_data)
        origin_data = origin_data["data"]["assets"]

        symbol_id = {item["symbol"]: item["id"] for item in origin_data}
        id_symbol = {item["id"]: item["symbol"] for item in origin_data}
        return symbol_id, id_symbol

    def get_id(self, symbol):
        symbol_id, id_symbol = self.assets()
        return symbol_id.get(symbol)

    def get_symbol(self, asset_id):
        symbol_id, id_symbol = self.assets()
        return id_symbol.get(asset_id)

    def output(self, symbol, percent=0.01):
        _paris = self.paris_symbol(symbol)
        amount = 0
        lines = []
        for baseid, quoteid in _paris:
            data = self.pair(baseid, quoteid)
            if not data:
                continue
            base = self.get_symbol(baseid)
            quote = self.get_symbol(quoteid)
            base_amount = float(data["base_amount"])
            quote_amount = float(data["quote_amount"])
            if base == symbol:
                iamount = base_amount
            else:
                iamount = quote_amount

            amount += iamount
            if base_amount != 0:
                price = round(quote_amount / base_amount, 2)
            else:
                price = 0
            if price < 1:
                if quote_amount != 0:
                    price = round(base_amount / quote_amount, 2)
                else:
                    price = 0
                line = (round(iamount, 2), f" {base}/{quote} 汇率 {price}")
            else:
                line = (round(iamount, 2), f"{quote}/{base} 汇率 {price}")
            lines.append(line)

        amount = round(amount, 2)
        lines.sort(key=lambda item: item[0], reverse=True)
        lines = [line for line in lines if line[0] / amount >= percent]

        text = (
            f"=== {symbol} 流动池@4swap ===\n【{amount}】小计\n"
            + "\n".join([f"【{line[0]}】{line[1]}" for line in lines])
            + "\n"
            + str(datetime.datetime.now())[:19]
        )
        return text


if __name__ == "__main__":
    symbol = "RUM"
    SwapPrice().output(symbol)
