import os

import praw


class RedditBot:
    
    def __init__(self):
        username = os.environ.get('REDDIT_USERNAME')
        password = os.environ.get('REDDIT_PASSWORD')
        client_id = os.environ.get('CLIENT_ID')
        secret = os.environ.get('CLIENT_SECRET')
        
        version = 0.1
        user_agent = f"web:pcpp-helper-bot:v{version} (by u/pcpp-helper-bot)"
        
        self.reddit = praw.Reddit(user_agent=user_agent,
                                  client_id=client_id, client_secret=secret,
                                  username=username, password=password)
        
        # Only look at submissions with one of these flairs
        self.pertinent_flairs = ["Build Complete", "Build Upgrade",
                                 "Build Help", "Build Ready"]

    def monitor_subreddit(self, subreddit_name):
        subreddit = self.reddit.subreddit(subreddit_name)
        
        for submission in subreddit.stream.submission():
            flair = submission.link_flair_text
            
            if flair and flair in self.pertinent_flairs:
                