import unittest
import logging

from pcpphelperbot import PCPPHelperBot
from postparsing import parse_submission


def read_file(filepath):
    with open(filepath, 'r') as file:
        text = file.read().strip()
    
    return text


class FakeSubmission:
    def __init__(self, id, flair=None):
        self.id = str(id)
        self.link_flair_text = flair
        self.is_self = True
        self.url = 'www.test.com'
        self.selftext_html = ''
        self.selftext = ''


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.f_handler = logging.FileHandler(f'../logs/bot_tests.log', mode='w', encoding='utf-8')
        self.bot = PCPPHelperBot(self.f_handler)
        
    @classmethod
    def tearDownClass(self):
        self.f_handler.close()
        

    def test_already_replied(self):
        reply_id = 456
        posted_time = 1610990729
        submission_id = 999
        submission_flair = None
        submission_url = "http://testing.com/sub/123"
        submission_time = 1610990729
        list_url = "http://listing.com/list/123"
        had_identifiable = True
        bad_markdown = False
        bad_html = 2
        missing_table = True
        tables_made = 2

        self.bot.db_handler.insert_reply(reply_id,
                             posted_time,
                             submission_id,
                             submission_flair,
                             submission_url,
                             submission_time,
                             list_url,
                             had_identifiable,
                             bad_markdown,
                             bad_html,
                             missing_table,
                             tables_made)
        
        sub = FakeSubmission(999, 'Build Ready')
        unpaired_urls, iden_anon, table_data = self.bot.read_submission(sub)
        
        self.assertEqual(0, len(unpaired_urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(0, table_data['total'])
        
    def test_reply_not_empty_anon(self):
        pcpp_urls = ['https://pcpartpicker.com/list/ZqWwj2']
        iden_urls = []
        data = {'total': 0, 'valid': 0, 'invalid': 0, 'bad_markdown': False}
        
        msg = self.bot.reply(None, pcpp_urls, iden_urls, data)
        self.assertIsNotNone(msg)
        self.assertNotEqual(0, len(msg))

    def test_reply_not_empty_iden(self):
        pcpp_urls = ['https://pcpartpicker.com/list/ZqWwj2']
        iden_urls = [('https://pcpartpicker.com/user/pcpp-helper-bot/saved/sH3ZJx',
                      'https://pcpartpicker.com/user/pcpp-helper-bot/saved/sH3ZJx')]
        data = {'total': 0, 'valid': 0, 'invalid': 0, 'bad_markdown': False}
    
        msg = self.bot.reply(None, pcpp_urls, iden_urls, data)
        self.assertIsNotNone(msg)
        self.assertNotEqual(0, len(msg))

    def test_reply_iden_valid_table(self):
        pcpp_urls = ['https://pcpartpicker.com/list/ZqWwj2']
        iden_urls = [('https://pcpartpicker.com/user/pcpp-helper-bot/saved/sH3ZJx',
                      'https://pcpartpicker.com/user/pcpp-helper-bot/saved/sH3ZJx')]
        data = {'total': 1, 'valid': 1, 'invalid': 0, 'bad_markdown': False}
    
        msg = self.bot.reply(None, pcpp_urls, iden_urls, data)
        self.assertIsNotNone(msg)
        self.assertNotEqual(0, len(msg))


if __name__ == '__main__':
    unittest.main()
