# coin_price

a bot: 

- get price from coinmarketcap or 4swap(mixin network),
- and post to quorum groups.

### How to use?

1. create `config.py` in [./scripts](./scripts):

```py
# scripts/config.py

# coinmarketcap 的密钥
CMC_PRO_API_KEY = "your-api-key-of-coinmarketcap"

groups = {
    "715872e2-cc31-4929-adcb-832676ad3d30": { # group_id you need to post price info.
        "coins": ["RUM", "BTC"], # coins to post.
        "minutes": 10, # post every 10 minutes.
    },
}

```

you should join the group which to post price info.

2. install these repos and put rumpy/officepy to PYTHONPATH;

- [seeds](https://github.com/liujuanjuan1984/seeds)
- [rumpy](https://github.com/liujuanjuan1984/rumpy)
- [officepy](https://github.com/liujuanjuan1984/officepy)

3.  run the quorum (binary or app) , and update the rumpyconfig.py;

4. finally, run the scripts:

```sh
python scripts/rum.py
```

<!--

长时间运行可能会遭遇某些报错而退出（知识点：定时调度）。

有另外一种可选方式为：windows 设定任务计划程序，为 `scripts/example_once.py`创建新任务，一次性，每 10 分钟一次，无限期。

-->

Try it!