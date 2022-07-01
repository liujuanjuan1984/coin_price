import datetime
import json
import os

import requests
from officy import Dir, JsonFile

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
Dir(data_dir).check()


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
        self.pairsdata = self.pairs()
        self.symbol_id, self.id_symbol = self.assets()

    def pairs(self):
        pairsfile = os.path.join(this_dir, "data", "pairs.json")
        if os.path.exists(pairsfile):
            origin_data = JsonFile(pairsfile).read()
        else:
            origin_data = self.session.get(f"{self.baseurl}/pairs").json()
            if origin_data:
                JsonFile(pairsfile).write(origin_data)

        origin_data = origin_data["data"]["pairs"]

        return [(item["base_asset_id"], item["quote_asset_id"]) for item in origin_data]

    def pairs_of_assetid(self, asset_id):
        return [item for item in self.pairs() if asset_id in item]

    def paris_of_symbol(self, symbol):
        return self.pairs_of_assetid(self.get_id(symbol))

    def pair(self, base_asset_id, quote_asset_id):
        api = f"{self.baseurl}/pairs/{base_asset_id}/{quote_asset_id}"
        try:
            data = self.session.get(api).json()["data"]
            return data
        except Exception as e:
            print(e)
            return {}

    def pair_by_symbol(self, base_symbol, quote_symbol):
        return self.pair(self.get_id(base_symbol), self.get_id(quote_symbol))

    def assets(self):
        assetsfile = os.path.join(this_dir, "data", "assets.json")
        if os.path.exists(assetsfile):
            origin_data = JsonFile(assetsfile).read()
        else:
            origin_data = self.session.get(f"{self.baseurl}/assets").json()
            if origin_data:
                JsonFile(assetsfile).write(origin_data)

        origin_data = origin_data["data"]["assets"]

        symbol_id = {item["symbol"]: item["id"] for item in origin_data}
        id_symbol = {item["id"]: item["symbol"] for item in origin_data}
        return symbol_id, id_symbol

    def get_id(self, symbol):
        return self.symbol_id.get(symbol)

    def get_symbol(self, asset_id):
        return self.id_symbol.get(asset_id)

    def _pair_price_by_symbol(self, base, quote):
        return self._pair_price(self.get_id(base), self.get_id(quote))

    def _pair_price(self, baseid, quoteid, sum_assetid=None):
        data = self.pair(baseid, quoteid)
        base_amount = float(data["base_amount"])
        quote_amount = float(data["quote_amount"])
        if base_amount * quote_amount == 0:
            return ("error", "error", 0), ("error", 0)
        base_amount = float(data["base_amount"])
        quote_amount = float(data["quote_amount"])
        quote = self.get_symbol(data["quote_asset_id"])
        base = self.get_symbol(data["base_asset_id"])

        if base_amount >= quote_amount:
            # 交易对是 quote/base
            price = (quote, base, base_amount / quote_amount)
            # print(price)
        else:
            price = (base, quote, quote_amount / base_amount)
            # print(price)

        if sum_assetid == None:
            sum_assetid = min(base_amount, quote_amount)

        if baseid == sum_assetid:
            amount = (base, base_amount)
        else:
            amount = (quote, quote_amount)

        return price, amount

    def _pool(self, asset_id, percent=0.01):
        print(datetime.datetime.now(), "_pool", asset_id, "start...")
        _paris = self.pairs_of_assetid(asset_id)

        amount = 0
        lines = []
        for baseid, quoteid in _paris:

            price, iamount = self._pair_price(baseid, quoteid, asset_id)

            line = (
                round(iamount[1], 2),
                f"{price[0]}/{price[1]} 汇率 {round(price[2],2)}",
            )
            amount += iamount[1]
            lines.append(line)

        amount = round(amount, 2)
        lines.sort(key=lambda item: item[0], reverse=True)
        lines = [line for line in lines if line[0] / amount >= percent]

        text = (
            f"=== {self.get_symbol(asset_id)} 流动池@4swap ===\n【{amount}】小计\n"
            + "\n".join([f"【{line[0]}】{line[1]}" for line in lines])
            + "\n"
            + str(datetime.datetime.now())[:19]
        )
        return text

    def pool(self, symbol, percent=0.01):
        """symbol 在 4swap 的流动池；某交易对的 symbol 数量占比低于 percent则不打印出来，当然会技术"""
        return self._pool(self.get_id(symbol), percent)

    def _rate(self, base, quote, bridge="XIN"):

        price1, _ = self._pair_price_by_symbol(base, bridge)
        price2, _ = self._pair_price_by_symbol(quote, bridge)
        if price1[2] * price2[2] == 0:
            return "", "", 0
        # base/bridge
        if price1[1] != bridge:
            price1 = (price1[1], price1[0], 1 / price1[2])
        # quote/bridge
        if price2[1] != bridge:
            price2 = (price2[1], price2[0], 1 / price2[2])
        # quote/base
        price = round(price2[2] / price1[2], 2)
        print(f"{quote}/{base} {price}")

        return quote, base, price

    def rum_rate(self, symbol="RUM", bridge="XIN"):
        pricefile = os.path.join(this_dir, "data", f"price_{symbol}.json")
        prices = JsonFile(pricefile).read({})
        quotes = ["BTC", "ETH", "BOX", "MOB", "EOS"]
        texts = f"=== {symbol} 汇率@4swap ===\n"

        for quote in quotes:
            q, b, p = self._rate(symbol, quote, bridge)
            if p != 0:
                texts += f"{q}/{b} {p}\n"
                key = f"{q}/{b}"
                if key not in prices:
                    prices[key] = {str(datetime.datetime.now()): p}
                else:
                    prices[key][str(datetime.datetime.now())] = p
        texts += str(datetime.datetime.now())[:19]
        JsonFile(pricefile).write(prices)
        return texts


if __name__ == "__main__":

    # 流动池
    r = SwapPrice().pool("XIN")
    print(r)
    # RUM 汇率
    r = SwapPrice().rum_rate()
    print(r)
