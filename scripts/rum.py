import os
import datetime
from time import sleep
from rumpyconfig import RumpyConfig
from officepy import JsonFile
from rumpy import RumClient
from config import groups
from coinmarketcap import prices
from swap import SwapPrice

bot = RumClient(**RumpyConfig.GUI)
progressfile = os.path.join(os.path.dirname(__file__), "progresss.json")
progress = JsonFile(progressfile).read({})
seeds = JsonFile(RumpyConfig.SEEDSFILE).read({})


def post(info):
    if not info:
        return print(info, "is null.check it.")

    for gid in groups:
        # join group if bot-node not in the group.
        if not bot.group.is_joined(gid):
            seed = seeds.get(gid)
            if seed:
                bot.group.join(seed)
            continue
        for coin in groups[gid]["coins"]:
            if coin not in info:
                continue

            can_post = False
            if gid not in progress:
                can_post = True
                progress[gid] = {}
            elif coin not in progress[gid]:
                can_post = True
                progress[gid][coin] = ""

            else:
                last_time = progress[gid][coin]
                m = groups[gid]["minutes"]
                next_time = datetime.datetime.strptime(
                    last_time, "%Y-%m-%d %H:%M:%S"
                ) + datetime.timedelta(minutes=m)

                while not can_post:
                    if datetime.datetime.now() > next_time:
                        can_post = True
                    else:
                        sleep(30)
            if can_post:
                for content in info[coin]["text"]:
                    resp = bot.group.send_note(group_id=gid, content=content)
                    print(resp)
                    progress[gid][coin] = f"{datetime.datetime.now()}"[:19]
                    JsonFile(progressfile).write(progress)


if __name__ == "__main__":
    s = SwapPrice()

    while True:
        info = prices()
        a, b = s.rum()
        info["RUM"] = {"text": [a, b]}
        post(info)
