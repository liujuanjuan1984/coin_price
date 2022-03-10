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

Try it!