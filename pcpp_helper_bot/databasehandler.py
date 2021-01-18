import os

from mysql.connector import connect, Error


# TODO: Best method to store in SQL?
class DatabaseHandler:
    """Handles connecting to, and writing/reading, a database
    that'll track the bot's replies. Mostly for not replying twice
    to submissions, but maybe some other data that may be useful for
    troubleshooting later."""
    
    def __init__(self):
        self.conn = None
    
    def connect(self):
        try:
            self.conn = connect(host="localhost",
                                user=os.environ.get("SQL_USER"),
                                password=os.environ.get("SQL_PASSWORD"),
                                database="buildapc_db"
                                )
            
            if self.conn.is_connected():
                print('Connected to MySQL Database')
        
        except Error as e:
            print(e)
    
    def disconnect(self):
        if self.conn.is_connected():
            self.conn.close()
        
        self.conn = None
    
    def create_table(self):
        # Replies table will hold the bot's replies and pertinent information
        
        create_replies_table = """
                                CREATE TABLE IF NOT EXISTS replies(
                                    reply_id BIGINT PRIMARY KEY,
                                    posted_time DATETIME,
                                    submission_id BIGINT,
                                    submission_flair VARCHAR(50),
                                    submission_url TEXT,
                                    submission_time DATETIME,
                                    list_url TEXT,
                                    had_identifiable BOOLEAN,
                                    bad_markdown BOOLEAN,
                                    bad_html INT,
                                    missing_table BOOLEAN,
                                    tables_made INT
                                )
                                """
        
        with self.conn.cursor() as cursor:
            cursor.execute(create_replies_table)
            self.conn.commit()
            
    def insert_reply(self, reply_id: int,
                     posted_time: int,
                     submission_id: int,
                     submission_flair: str,
                     submission_url: str,
                     submission_time: int,
                     list_url: str,
                     had_identifiable: bool,
                     bad_markdown: bool,
                     bad_html: int,
                     missing_table: bool,
                     tables_made: int):
        insert_reply = """
                        INSERT INTO replies (
                            reply_id,
                            posted_time,
                            submission_id,
                            submission_flair
                            submission_url,
                            submission_time,
                            list_url,
                            had_identifiable,
                            bad_markdown,
                            bad_html,
                            missing_table,
                            tables_made
                        )
                        VALUES
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        
        values = (reply_id, posted_time, submission_id,
                  submission_flair, submission_url, submission_time,
                  list_url, had_identifiable, bad_markdown, bad_html,
                  missing_table, tables_made)
        
        with self.conn.cursor() as cursor:
            cursor.execute(insert_reply, values)

    def select_reply(self, submission_id: int):
        """Search the database for replies with this submission id.
        
        Args:
            submission_id (int): Integer ID for a submission.
        
        Returns:
            A match, or None.
        """
        
        query = """SELECT
                    reply_id
                FROM
                    replies
                WHERE
                    submission_id = "%s"
                """ % submission_id
        
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()
