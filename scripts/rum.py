import os
import datetime
import time
import sched
from rumpy import RumClient
from config import groups
from coinmarketcap import CoinmarketcapPrice
from swap import SwapPrice


class Bot(RumClient):
    def init(self):
        self.swap = SwapPrice()
        self.cmk = CoinmarketcapPrice()
        self.progress = {}
        self.info = {}
        return self

    def _can_post(self, gid, coin):
        if gid not in self.progress:
            self.progress[gid] = {}
            return True
        elif coin not in self.progress[gid]:
            self.progress[gid][coin] = None
            return True
        else:
            last_time = self.progress[gid][coin]
            m = groups[gid]["minutes"]
            next_time = datetime.datetime.strptime(
                last_time, "%Y-%m-%d %H:%M:%S"
            ) + datetime.timedelta(minutes=m)

            if datetime.datetime.now() >= next_time:
                return True
            else:
                return False

    def _update_info(self, coin):

        if self.info.get(coin) == None:
            self.info[coin] = {}
        if "text" not in self.info[coin]:
            self.info[coin]["text"] = []

            # update price info from coinmarketcap if needed.
            # if coin in ["ETH", "BTC"]:
            #    self.info.update(self.cmk.price())

            swap = self.swap.pool(coin)
            if swap:
                self.info[coin]["text"].append(swap)

    def _post_to_rum(self):
        print(datetime.datetime.now(), "_post_to_rum", "start...")

        for gid in groups:
            # join group if bot-node not in the group.
            self.group_id = gid
            if not self.group.is_joined():
                continue

            for coin in groups[gid]["coins"]:
                if not self._can_post(gid, coin):
                    continue

                self._update_info(coin)

                for content in self.info[coin]["text"]:
                    print(content)
                    resp = self.group.send_note(content=content)
                    print(resp)
                    if "trx_id" in resp:
                        self.progress[gid][coin] = f"{datetime.datetime.now()}"[:19]
                        self.info[coin] = None

        self.post_to_rum()
        print(datetime.datetime.now(), "_post_to_rum", "done.")

    def post_to_rum(self):
        """this function could not work well always. maybe here are some bugs."""
        print(datetime.datetime.now(), "post_to_rum", "init ...")
        s = sched.scheduler(time.time, time.sleep)
        print(datetime.datetime.now(), "post_to_rum", "enter ...")
        s.enter(60, 1, self._post_to_rum, ())
        print(datetime.datetime.now(), "post_to_rum", "run ...")
        s.run()
        print(datetime.datetime.now(), "exit?!!!")

    def once_post(self):
        for gid in groups:
            # join group if bot-node not in the group.
            self.group_id = gid
            if not self.group.is_joined():
                continue

            for coin in groups[gid]["coins"]:
                self._update_info(coin)

                for content in self.info[coin]["text"]:
                    print(content)
                    resp = self.group.send_note(content=content)
                    print(resp)
                    if "trx_id" in resp:
                        self.info[coin] = None
