import os
import re
import logging

import praw

from tablecreator import TableCreator
from postparsing import detect_pcpp_html_elements, count_well_formed_tables
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
        
        with open('./templates/replytemplate.md', 'r') as template:
            self.REPLY_TEMPLATE = template.read()
        
        with open('.templates/idenlinkfound.md', 'r') as template:
            self.IDENTIFIABLE_TEMPLATE = template.read()
    
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
            
            # Only look at text submissions and with the appropriate flairs
            if flair in self.pertinent_flairs and submission.is_self:
                pcpp_elements = detect_pcpp_html_elements(submission.selftext_html)
                
                self.all_log.info(f"SUBMISSION: {submission.title} AT {submission.url}")
                self.all_log.info(f"SUBMISSION TEXT: {submission.selftext}")
                
                links_to_post, had_identifiable = self._find_reply_data(pcpp_elements)
                
                # TODO: EDIT BELOW
                """
                if len(pcpp_elements['table_head']) == 0 and \
                        len(pcpp_elements['table_foot']) == 0:
                    
                    self.all_log.info("NO TABLE")
                    
                    pcpp_url = None
                    if len(pcpp_elements['anon']) != 0:
                        pcpp_url = pcpp_elements['anon'][0]
                        self.replied_log.info(f"ANONYMOUS LINK FOUND: {pcpp_url}")
                    
                    elif len(pcpp_elements['iden']) != 0:
                        iden_url = pcpp_elements['iden'][0]
                        self.replied_log.info(f"IDENTIFIABLE LINK FOUND: {iden_url}")
                        pcpp_url = self.pcpp_parser.get_anon_list_url(iden_url)
                        self.replied_log.info(f"ANONYMOUS LINK FOUND AFTER IDEN: {pcpp_url}")
                    
                    if pcpp_url:
                        self._reply_with_table(pcpp_url, submission)
                else:
                    self.all_log.info("TABLE FOUND")
                """
    
    def _find_reply_data(self, pcpp_elements: dict):
        """Finds data needed to make a reply, such as PCPP links without tables
        and if identifiable links were used.
        
        Args:
            pcpp_elements (dict(Lists)): Dictionary of PCPP elements found in the post.
            
        Returns:
            A tuple of links that need tables and if there were identifiable
            links used in the post.
        """
        
        valid_tables, invalid_tables = \
            count_well_formed_tables(pcpp_elements['table_headers'],
                                     pcpp_elements['table_footers'])
        all_pcpp_links = set()
        found_identifiable = len(pcpp_elements['iden']) != 0
        
        # Get the anonymous urls from the identifiable links
        if found_identifiable:
            for iden_url in pcpp_elements['iden']:
                all_pcpp_links.add(self.pcpp_parser.get_anon_list_url(iden_url))
        
        # Combine anonymous urls with the ones from the identifiable links
        if len(pcpp_elements['anon']) != 0:
            anon_links = {a['href'] for a in pcpp_elements['anon']}
            all_pcpp_links += anon_links
        
        # Figure out which list urls may not have an accompanied table
        links_to_post = self._get_lists_to_post(all_pcpp_links,
                                                pcpp_elements['pcpp_headers'],
                                                valid_tables)
        
        return links_to_post, found_identifiable
    
    def _get_lists_to_post(self, links: list, headers: list, valid_tables: int):
        """Determine which links need to be tables by assuming if there are
        valid tables, then they have matching headers. Links from the headers
        are likely coupled with a valid table."""
        
        link_count = len(links)
        
        if link_count != 0:
            # Likely the headers are paired with the valid tables, so remove
            # any links that were already covered by a table
            if valid_tables != 0 and headers != 0:
                header_links = {a['href'] for a in headers}
                links -= header_links
            
            return links
    
    def _reply_with_table(self, pcpp_url: str, submission: praw.reddit.Submission):
        """Replies to the submission with a Markup table with the components
        from the PC Part Picker list URL.
        
        Args:
            pcpp_url (str): PC Part Picker list URL
            submission (:obj"`PRAW.Reddit.Submission`): A Submission object from PRAW

        Returns:
            PRAW Comment object representing the reply, or None.
        """
        
        if not pcpp_url:
            print(f"No url, or had table from {submission.title}")
            return None
        else:
            # TODO: Hand submission data to TableCreator
            html_doc = self.pcpp_parser.request_page_data(pcpp_url)
            parts_list, total = self.pcpp_parser.parse_page(html_doc)
            
            if parts_list:
                table = self.table_creator.create_markup_table(pcpp_url,
                                                               parts_list,
                                                               total)
                
                self.replied_log.info(f"TABLE CREATED:\n {table}")
                return None  # TODO: Return the Reply object
    
    @staticmethod
    def detect_pcpp_elements(text):
        """Detects PC Part Picker tables, anonymous lists, and
        identifiable lists in the provided text.

        Args:
            text (str): Text of a submission (or comment) from Reddit.

        Returns:
            A dictionary of sets with the following keys: anon, table_head,
            table_foot, and iden . Anon holds anonymous list urls,
            table_head & foot contain the header and footer of properly
            formatted tables, and iden holds identifiable urls.
        """
        
        pcpp_elements = {'anon': [], 'table_head': [], 'table_foot': [], 'iden': []}
        
        # TODO: Look for newline characters (\n) between rows? Also breaks it
        # TODO: Combine into looking for the entire table?
        proper_table_head_pat = r"(?P<table_head>\[PCPartPicker Part List\])\((?P<table_url>https://pcpartpicker.com/list/\w+)\)"
        proper_table_foot_pat = r"(?P<table_foot>Generated by \[PCPartPicker\])"
        
        anon_list_pat = r"(?P<anon>https://pcpartpicker.com/list/\w+)"
        identifiable_list_pat = r"\((?P<iden>https://pcpartpicker.com/user/.+)\)"
        
        patterns = "|".join([proper_table_head_pat, proper_table_foot_pat, anon_list_pat, identifiable_list_pat])
        pcpp_elements_re = re.compile(patterns)
        
        for m in pcpp_elements_re.finditer(text):
            if m.group('anon'):
                pcpp_elements['anon'].append(m.group('anon'))
            if m.group('table_head'):
                pcpp_elements['table_head'].append((m.group('table_url'), (m.group('table_head'))))
            if m.group('table_foot'):
                pcpp_elements['table_foot'].append((m.group('table_foot')))
            if m.group('iden'):
                iden_url = m.group('iden')
                # Different view of the page that we don't want
                iden_url.replace("#view=", '')
                
                pcpp_elements['iden'].append(iden_url)
        
        return pcpp_elements
