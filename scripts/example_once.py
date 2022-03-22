from rum import Bot
from swap import SwapPrice
from rumpyconfig import RumpyConfig

bot = Bot(**RumpyConfig.GUI).init()
bot.once_post()

texts = SwapPrice().rum_rate()
bot.group_id = "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436"
bot.group.send_note(content=texts)
