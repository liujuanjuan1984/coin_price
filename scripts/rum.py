import os
import datetime
import time
import sched
from rumpyconfig import RumpyConfig
from officepy import JsonFile
from rumpy import RumClient
from config import groups
from coinmarketcap import CoinmarketcapPrice
from swap import SwapPrice


class Bot(RumClient):
    progressfile = os.path.join(os.path.dirname(__file__), "progresss.json")

    def _can_post(self, gid, coin, progress):
        if gid not in progress:
            return True
        elif coin not in progress[gid]:
            return True
        else:
            last_time = progress[gid][coin]
            m = groups[gid]["minutes"]
            next_time = datetime.datetime.strptime(
                last_time, "%Y-%m-%d %H:%M:%S"
            ) + datetime.timedelta(minutes=m)

            if datetime.datetime.now() >= next_time:
                return True
            else:
                return False

    def _update_info(self, coin, info):

        if info.get(coin) == None:
            info[coin] = {}
        if "text" not in info[coin]:
            info[coin]["text"] = []

            if coin in ["ETH", "BTC"]:
                xinfo = CoinmarketcapPrice().price()
                info.update(xinfo)

            swap = SwapPrice().output(coin)
            if swap:
                info[coin]["text"].append(swap)
        return info, len(info[coin]["text"]) > 0

    def _update_progress(self, gid, coin, progress):

        if gid not in progress:
            progress[gid] = {}
        progress[gid][coin] = f"{datetime.datetime.now()}"[:19]
        JsonFile(self.progressfile).write(progress)
        return progress

    def _post_to_rum(self, info=None, progress=None):
        info = info or {}
        seeds = JsonFile(RumpyConfig.SEEDSFILE).read({})
        progress = progress or JsonFile(self.progressfile).read({})

        for gid in groups:
            # join group if bot-node not in the group.
            self.group_id = gid
            if not self.group.is_joined():
                seed = seeds.get(gid)
                if seed:
                    self.group.join(seed)
                continue

            for coin in groups[gid]["coins"]:
                info, flag = self._update_info(coin, info)
                if not flag:
                    continue

                flag = self._can_post(gid, coin, progress)
                if not flag:
                    continue

                for content in info[coin]["text"]:
                    print(content)
                    resp = self.group.send_note(content=content)
                    print(resp)
                    if "trx_id" in resp:
                        progress = self._update_progress(gid, coin, progress)
                        info[coin] = None

        self.post_to_rum()
        return info

    def post_to_rum(self):
        print(datetime.datetime.now(), "working ...")
        s = sched.scheduler(time.time, time.sleep)
        s.enter(60, 1, self._post_to_rum, ())
        s.run()
        print(datetime.datetime.now(), "exit?!!!")


if __name__ == "__main__":
    Bot(**RumpyConfig.GUI).post_to_rum()
