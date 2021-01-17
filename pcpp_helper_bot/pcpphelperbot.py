import os
import re
import logging

import praw

from tablecreator import TableCreator
from postparsing import parse_submission
from pcpp.pcppparser import PCPPParser


class PCPPHelperBot:
    """Posts PC Part Picker markup tables when applicable.
    
    This utilizes the PRAW wrapper for interacting with Reddit. It streams
    new submissions in order to look for submissions with a PC Part Picker
    list URL. If the post already has a table, no action will be taken. If
    not, or it is malformed, a reply containing the table will be posted.
    """
    
    def __init__(self, all_log: logging.Logger, replied_log: logging.Logger):
        self.replied_log = replied_log
        self.all_log = all_log
        
        self.replied_log.info("STARTING")
        self.all_log.info("STARTING")
        
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
        self.pertinent_flairs = ["Build Complete", "Build Upgrade",
                                 "Build Help", "Build Ready", None]
        
        self.pcpp_parser = PCPPParser()
        self.table_creator = TableCreator()
        self.MAX_TABLES = 2
        
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
        
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # Stream in new submissions from the subreddit
        for submission in subreddit.stream.submissions():
            flair = submission.link_flair_text
            # TODO: Check if replied already to this post
            
            # Only look at text submissions and with the appropriate flairs
            if flair in self.pertinent_flairs and submission.is_self:
                self.all_log.info(f"SUBMISSION: {submission.title} AT {submission.url}")
                self.all_log.info(f"SUBMISSION TEXT: {submission.selftext}")
                
                # Parse pertinent info from the submission
                tableless_urls, iden_anon_urls, table_data \
                    = parse_submission(submission.selftext_html, submission.selftext)
                
                # If there are missing/broken tables or identifiable links
                if len(tableless_urls) != 0 or len(iden_anon_urls) != 0:
                    # Create the reply with this information
                    reply_message = self._make_reply(tableless_urls,
                                                     iden_anon_urls,
                                                     table_data)
                    print(reply_message)
                    # Post the reply!
                    # submission.reply(reply_message)
    
    def _make_reply(self, tableless_urls, iden_anon_urls, table_data):
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
        
        reply_message = self._put_message_together(table_markdown,
                                                   iden_markdown)
        
        return reply_message
    
    def _put_message_together(self, table_markdown, iden_markdown):
        """Puts together the variable data into a message.
        
        Args:
            table_markdown (str): Contains the markdown for the table data.
            iden_markdown (str): Contains the markdown for the identifiable
                                    message and data.
                                    
        Returns:
            A string containing the combined reply message.
        """
        
        reply_message = None
        message_markdown = []
        
        if len(table_markdown) != 0:
            message_markdown.append(table_markdown)
        
        if iden_markdown:
            message_markdown.append(iden_markdown)
        
        if len(message_markdown) != 0:
            message_markdown = '\n\n'.join(message_markdown)
            reply_message = self.REPLY_TEMPLATE.replace(':message:', message_markdown)
        
        return reply_message
    
    def _make_table_markdown(self, urls, table_data):
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
                table_markdown = self.table_creator.create_markup_table(pcpp_url, parts_list, total)
                all_table_markdown.append(table_markdown)
            
            # Put the table(s) together
            all_table_markdown = '\n\n'.join(all_table_markdown)
            
            # Check which issue(s) occurred (at least one will match)
            if table_data['total'] == 0:
                issues.append("a missing table")
            if table_data['invalid'] != 0:
                issues.append("a broken/partial table")
            if table_data['bad_markdown']:
                issues.append("escaped markdown")
            
            issues_markdown = ','.join(issues)
            
            # Input the message data into the template
            table_message = self.TABLE_TEMPLATE.replace(':issues:', issues_markdown)
            table_message = table_message.replace(':table:', all_table_markdown)
        
        return table_message
    
    def _make_identifiable_markdown(self, iden_anon_urls):
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
                list_items.append(f'* [{iden_url}] &#8594; [{anon_url}]')
            
            list_markdown = '\n'.join(list_items)
            
            # Put the list into the template
            iden_markdown = self.IDENTIFIABLE_TEMPLATE.replace(':urls:', list_markdown)
        
        return iden_markdown
