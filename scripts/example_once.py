from rum import Bot
from rumpyconfig import RumpyConfig

bot = Bot(**RumpyConfig.GUI).init()
bot.once_post()
