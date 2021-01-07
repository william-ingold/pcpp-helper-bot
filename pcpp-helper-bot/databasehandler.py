import os

from getpass import getpass
from mysql.connector import connect, Error


# TODO: Best method to store in SQL?
class DatabaseHandler:
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
    
    def create_tables(self):
        # Replies table will hold the bot's replies and pertinent information
        create_replies_table = """
                                CREATE TABLE IF NOT EXISTS replies(
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    reply_id BIGINT,
                                    replied_to_id BIGINT,
                                    was_comment TINYINT,
                                    posted_time DATETIME,
                                    score INT,
                                    submission_flair VARCHAR(50),
                                    submission_url TEXT,
                                    submission_time DATETIME,
                                    list_url TEXT
                                )
                                """
        
        # Components table will hold all the components from each list
        create_components_table = """
                                    CREATE IF NOT EXISTS components(
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        reply_id BIGINT,
                                        component_type VARCHAR(50),
                                        component_name TEXT,
                                        pcpp_url TEXT,
                                        price FLOAT,
                                        vendor VARCHAR(50),
                                        region VARCHAR(5),
                                        list_url TEXT
                                        FOREIGN KEY(reply_id) REFERENCES replies(reply_id)
                                    )
                                    """
        
        with self.conn.cursor() as cursor:
            cursor.execute(create_replies_table)
            cursor.execute(create_components_table)
            self.conn.commit()
            
    def insert_reply(self, reply_id, replied_to_id, was_comment, posted_time,
                     submission_flair, submission_url, submission_time,
                     list_url, score = 1):
        insert_reply = """
                        INSERT INTO replies (
                            reply_id,
                            replied_to_id,
                            was_comment,
                            posted_time
                            score,
                            submission_flair
                            submission_url,
                            submission_time,
                            list_url
                        )
                        VALUES
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        
        values = (reply_id, replied_to_id, was_comment, posted_time,
                  submission_flair, submission_url, submission_time,
                  list_url, score)
        
        with self.conn.cursor() as cursor:
            cursor.execute(insert_reply, values)
