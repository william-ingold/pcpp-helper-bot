import unittest
import logging

from pcpphelperbot import PCPPHelperBot
from databasehandler import DatabaseHandler
from postparsing import parse_submission


def read_file(filepath):
    with open(filepath, 'r') as file:
        text = file.read().strip()
    
    return text


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.db = DatabaseHandler()
        self.db.connect()
        self.db.create_table()

        self.f_handler = logging.FileHandler(f'../logs/bot_tests.log', mode='w', encoding='utf-8')

        self.bot = PCPPHelperBot(self.f_handler)
        
    @classmethod
    def tearDownClass(self):
        self.db.disconnect()
        self.f_handler.close()
        
    def test_database_insert_read(self):
        reply_id = 123
        posted_time = 1610990729
        submission_id = 456
        submission_flair = None
        submission_url = "http://testing.com/sub/123"
        submission_time = 1610990729
        list_url = "http://listing.com/list/123"
        had_identifiable = True
        bad_markdown = False
        bad_html = 2
        missing_table = True
        tables_made = 2
        
        self.db.insert_reply(reply_id,
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
        
        reply = self.db.select_reply(456)
        
        self.assertIsNotNone(reply)


if __name__ == '__main__':
    unittest.main()
