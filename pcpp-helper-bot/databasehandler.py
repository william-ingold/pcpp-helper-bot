import os

from getpass import getpass
from mysql.connector import connect, Error


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
