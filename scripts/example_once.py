from rum import Bot
from rumpy import FullNode

rum_client = FullNode(port=62663, crtfile=r"C:\certs\server.crt")
bot = Bot(rum_client)
bot.once_post()

texts = bot.swap.rum_rate()
group_id = "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436"
rum_client.api.send_note(group_id=group_id, content=texts)
