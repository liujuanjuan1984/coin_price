from rum import Bot

params = {"port": 62663, "crtfile": r"C:\certs\server.crt"}

bot = Bot(params).init()
bot.once_post()

texts = bot.swap.rum_rate()
bot.group_id = "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436"
bot.group.send_note(content=texts)
