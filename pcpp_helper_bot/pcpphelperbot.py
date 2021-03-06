import os
import logging
from datetime import datetime

import praw
from praw.models import Message
import mysql.connector.errors as mysql_errors

from tablecreator import TableCreator
from postparsing import parse_submission
from pcpp.pcppparser import PCPPParser
from databasehandler import DatabaseHandler


class PCPPHelperBot:
    """Posts PC Part Picker markup tables when applicable.
    
    This utilizes the PRAW wrapper for interacting with Reddit. It streams
    new submissions in order to look for submissions with a PC Part Picker
    list URL. If the post already has a table, no action will be taken. If
    not, or it is malformed, a reply containing the table will be posted.
    """
    
    def __init__(self, log_file_handler, live=False):
        self.is_live = live
        
        # Logger setup
        if self.is_live:
            self.logger = logging.getLogger('PCPPHelperBot')
        else:
            self.logger = logging.getLogger('PCPPHelperBot-DEBUG')
            
        self.logger.addHandler(log_file_handler)
        now_str = datetime.now().strftime('%H:%M:%S')
        self.logger.info(f'STARTING {now_str}')
        
        # Database setup
        if self.is_live:
            self.db_handler = DatabaseHandler()
        else:
            self.db_handler = DatabaseHandler(debug=True)
        
        self.db_handler.connect()
        self.db_handler.create_table()

        # Retrieve environment vars for secret data
        username = os.environ.get('REDDIT_USERNAME')
        password = os.environ.get('REDDIT_PASSWORD')
        client_id = os.environ.get('CLIENT_ID')
        secret = os.environ.get('CLIENT_SECRET')
        
        version = 0.1
        user_agent = f"web:pcpp-helper-bot:v{version} (by u/pcpp-helper-bot)"
        
        # Utilize PRAW wrapper
        self.reddit = praw.Reddit(user_agent=user_agent,
                                  client_id=client_id, client_secret=secret,
                                  username=username, password=password)
        
        # Only look at submissions with one of these flairs
        # TODO: Are these the best submission flairs to use?
        self.pertinent_flairs = ['Build Complete', 'Build Upgrade',
                                 'Build Help', 'Build Ready', None]
        
        self.pcpp_parser = PCPPParser(log_file_handler)
        self.table_creator = TableCreator()
        self.MAX_TABLES = 2
        self.subreddit_name = None
        
        # Read in the templates
        with open('./templates/replytemplate.md', 'r') as template:
            self.REPLY_TEMPLATE = template.read()
        
        with open('./templates/idenlinkfound.md', 'r') as template:
            self.IDENTIFIABLE_TEMPLATE = template.read()
        
        with open('./templates/tableissuetemplate.md', 'r') as template:
            self.TABLE_TEMPLATE = template.read()
    
    def monitor_subreddit(self, subreddit_name: str):
        """Monitors the subreddit provided (mainly r/buildapc) for new
        submissions.
        
        Args:
            subreddit_name (str): The name of the subreddit
        """
        continue_monitoring = True
        self.subreddit_name = subreddit_name
        
        # skip_existing will skip the posts made BEFORE the bot starts observing
        # By default, up to 100 historical submissions/comments would be returned
        # See PRAW.reddit.SubredditStream #3147
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # Stream in new submissions from the subreddit
        while continue_monitoring:
            try:
                for submission in subreddit.stream.submissions(skip_existing=True):
                    unpaired_urls, iden_anon_urls, table_data = self.read_submission(submission)
                    
                    # If there are missing/broken tables or identifiable links
                    if len(unpaired_urls) != 0 or len(iden_anon_urls) != 0:
                        self.logger.info('FOUND TABLELESS OR IDENTIFIABLE URLS')
                        self.logger.info(f'SUBMISSION TEXT: {submission.selftext}')
                        
                        self.reply(submission, unpaired_urls, iden_anon_urls, table_data)

                    should_stop, reason = self._check_inbox_for_stop()
                    if should_stop:
                        self.logger.info(f'STOPPING BY REQUEST. REASON: {reason}')
                        continue_monitoring = False
                        break
                        
            except Exception as e:
                self.logger.critical('Problem connecting to Reddit or in creating reply')
                self.logger.critical('Exception data: ', exc_info=True)
                
            # TODO: Catch any exceptions for when Reddit is down or PRAW has issues
        self._cleanup_database()

    def read_submission(self, submission: praw.reddit.Submission):
        """Reads a submission from Reddit.
        
        Args:
            submission ('obj': praw.reddit.Submission): A PRAW Submission object.
        
        Returns:
            (urls without tables, (identifiable, anonymous) pair list,
            {'total', 'valid', 'invalid', 'bad_markdown'} dict  of table
            data).
        """
        
        flair = submission.link_flair_text
        tableless_urls = []
        iden_anon_urls = []
        table_data = {'total': 0, 'valid': 0, 'invalid': 0, 'bad_markdown': False}
    
        if self._already_replied(submission.id):
            self.logger.info('Already replied to this submission.')
    
        # Only look at text submissions and with the appropriate flairs
        elif flair in self.pertinent_flairs and submission.is_self:
            self.logger.info(f'CHECKING SUBMISSION: {submission.url}')
        
            # Parse pertinent info from the submission
            tableless_urls, iden_anon_urls, table_data \
                = parse_submission(submission.selftext_html, submission.selftext, self.pcpp_parser)
                
        return tableless_urls, iden_anon_urls, table_data
        
    def reply(self, submission, unpaired_urls, iden_anon_urls, table_data):
        """Replies to a Reddit submission.
        
        Args:
            submission (`obj`: praw.Reddit.Submission): PRAW Submission object.
            unpaired_urls (list): urls without an accompanying table.
            iden_anon_urls (list): Pairs of identifiable, anonymous list urls.
            table_data (dict): Holds information about table data in submission.
            
        Returns:
            Reply message string if NOT live, otherwise PRAW.reddit.Comment object.
        """
    
        # Create the reply with this information
        reply_message = self._make_reply(unpaired_urls,
                                        iden_anon_urls,
                                        table_data)
    
        # Only if the bot is 'live' on Reddit or not
        if self.is_live:
            # Post the reply!
            reply = submission.reply(reply_message)
            self._save_reply_db(reply, submission, table_data, iden_anon_urls, unpaired_urls)
            return reply
        else:
            return reply_message

    def _make_reply(self, tableless_urls: list, iden_anon_urls: list, table_data: dict):
        """Creates the full reply message.
        
        Args:
            tableless_urls (list): List of urls that don't have an accompanying
                                    table.
            iden_anon_urls (list): List of (identifiable, anonymous) urls found.
            table_data (dict): Dictionary describing the table data found
                                in the submission.
                                
        Returns:
            The entire reply message, ready to be posted.
        """
        
        table_markdown = self._make_table_markdown(tableless_urls, table_data)
        iden_markdown = self._make_identifiable_markdown(iden_anon_urls)
        
        if len(table_markdown) == 0 and len(tableless_urls) != 0:
            self.logger.error('Failed to make table markdown for urls: {tableless_urls}')
            
        if len(iden_anon_urls) != 0 and len(iden_markdown) == 0:
            self.logger.error(f'Failed to make identifiable markdown for urls: {iden_anon_urls}')
        
        reply_message = self._put_message_together(table_markdown,
                                                   iden_markdown)
        
        if len(reply_message) == 0:
            self.logger.error('Failed to create a message.')
        else:
            self.logger.info(f'Reply: {reply_message}')
        
        return reply_message
    
    def _put_message_together(self, table_markdown: str, iden_markdown: str):
        """Puts together the variable data into a message.
        
        Args:
            table_markdown (str): Contains the markdown for the table data.
            iden_markdown (str): Contains the markdown for the identifiable
                                    message and data.
                                    
        Returns:
            A string containing the combined reply message.
        """
        
        reply_message = ''
        message_markdown = []
        
        if len(table_markdown) != 0:
            message_markdown.append(table_markdown)
        
        if len(iden_markdown) != 0:
            message_markdown.append(iden_markdown)
        
        if len(message_markdown) != 0:
            message_markdown = '\n\n'.join(message_markdown)
            reply_message = self.REPLY_TEMPLATE.replace(':message:', message_markdown)
        
        return reply_message
    
    def _make_table_markdown(self, urls: list, table_data: dict):
        """Put together the table markdown. This could be up to self.MAX_TABLES.
        
        Args:
            urls (list): List of PCPP urls to make tables for.
            table_data (dict): Dictionary describing the table data found
                                in the submission.
            
        Returns:
            A string containing the markdown for the tables for the PCPP lists.
        """
        
        table_message = ''
        issues = []
        
        if urls and 0 < len(urls) <= self.MAX_TABLES:
            all_table_markdown = []
            
            # Create the table markup for each list url
            for pcpp_url in urls:
                list_html = self.pcpp_parser.request_page_data(pcpp_url)
                parts_list, total = self.pcpp_parser.parse_page(list_html)
                table_markdown = self.table_creator.create_markdown_table(pcpp_url, parts_list, total)
                all_table_markdown.append(table_markdown)
            
            # Put the table(s) together
            all_table_markdown = '\n\n\n'.join(all_table_markdown)
            
            lists_without_tables = abs(table_data['total'] - len(urls))
            # Check which issue(s) occurred (at least one will match)
            if table_data['total'] == 0 or lists_without_tables != 0:
                issues.append('a missing table')
            if table_data['invalid'] != 0:
                issues.append('a broken or partial table')
            if table_data['bad_markdown']:
                issues.append('escaped or broken markdown')
            
            issues_markdown = ', '.join(issues)
            
            # Input the message data into the template
            table_message = self.TABLE_TEMPLATE.replace(':issues:', issues_markdown)
            table_message = table_message.replace(':table:', all_table_markdown)
        
        return table_message
    
    def _make_identifiable_markdown(self, iden_anon_urls: list):
        """Creates the message for when identifiable list urls are found.
        
        Args:
            iden_anon_urls (list): List of (identifiable, anonymous) urls found.
            
        Returns:
            A string containing the markdown message for when identifiable
            urls are found.
        """
        
        iden_markdown = ''
        
        if iden_anon_urls and len(iden_anon_urls) > 0:
            list_items = []
            
            # Create a bullet point showing the anonymous list url for
            # each identifiable list url found.
            for iden_url, anon_url in iden_anon_urls:
                # identifiable -> anonymous
                list_items.append(f'* {iden_url} &#8594; {anon_url}')
            
            list_markdown = '\n'.join(list_items)
            
            # Put the list into the template
            iden_markdown = self.IDENTIFIABLE_TEMPLATE.replace(':urls:', list_markdown)
        
        return iden_markdown

    def _save_reply_db(self, reply: praw.reddit.Comment,
                      submission: praw.reddit.Submission,
                      table_data: dict,
                      iden_anon_urls: list,
                      urls: list):
        """Save the reply data into the database.
        
        Args:
            reply (PRAW.Reddit.Comment): The reply left by the bot
            submission (PRAW.Reddit.Submission): Submission the bot replied to
            table_data (dict): Holds data about the tables
            iden_anon_urls (list): List of identifiable links
            urls (list): List of the PCPP urls I made tables for
        """
        
        flair = submission.link_flair_text
        had_identifiable = len(iden_anon_urls) != 0
        missing_table = table_data['total'] == 0
        
        # Reddit id's are in base 36
        reply_id = int(reply.id, 36)
        submission_id = int(submission.id, 36)
    
        try:
            self.db_handler.insert_reply(reply_id, reply.created_utc,
                                         submission_id, flair,
                                         submission.url,
                                         submission.created_utc,
                                         str(urls),
                                         had_identifiable,
                                         table_data['bad_markdown'],
                                         table_data['invalid'],
                                         missing_table,
                                         len(urls)
                                         )
        except mysql_errors.IntegrityError as e:
            self.logger.error('MySql insertion error: %s', e.msg)
        
    def _cleanup_database(self):
        """Cleanup."""
        
        # Want to cleanup the table if just testing.
        if not self.is_live:
            self.db_handler.clear_table()

        self.db_handler.disconnect()

    def _already_replied(self, submission_id: str):
        """Check if the bot has replied already to this submission."""
        
        id_as_int = int(submission_id, 36)
        reply = self.db_handler.select_reply(id_as_int)
        
        return reply is not None
    
    def _check_inbox_for_stop(self):
        """Checks if a moderator messaged the bot to stop running.
        The subject must be 'stop', and the body of the message
        contains an optional reason for stopping the bot.
        
        Returns:
            (boolean on if to stop, a string containing the reason).
        """
        
        should_stop = False
        reason = ''
        
        for item in self.reddit.inbox.unread():
            # Check if it is a message, not a mention or something else
            if isinstance(item, Message):
                author = item.author
                
                # Check if the messenger is a moderator of r/buildapc
                if not author.is_suspended and author.is_mod and self.subreddit_name in author.moderated():
                    subject = item.subject
                    
                    # Did they tell me to stop?
                    if 'stop' in subject.lower():
                        reason = item.body
                        should_stop = True
                        item.mark_read()
                        
        return should_stop, reason
