import logging
import datetime

from pcpphelperbot import PCPPHelperBot

if __name__ == '__main__':
    # Logging file handler
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    f_handler = logging.FileHandler(f'../logs/{date}.log', mode='w', encoding='utf-8')
    
    bot = PCPPHelperBot(f_handler)
    bot.monitor_subreddit('buildapc')
    
    f_handler.close()
