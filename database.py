import mysql.connector
from mysql.connector import Error


class SQLHandler():
    def __init__(self):      
        try:
            self.connection = mysql.connector.connect(host='localhost',
                                                      database='traffic_watcha',
                                                      user='root',
                                                      password='')
        except Error as e:
            print("Error while connecting to MySQL", e)

    def add_density(self,value):
            insert_query = f"INSERT INTO density " \
                            "(density, classification, location, intersection, creation_time) " \
                           "VALUES (%s, %s, %s, %s, %s)"
            insert_query2 = f"INSERT INTO temp2 " \
                            "(density, classification, location, intersection, creation_time) " \
                           "VALUES (%s, %s, %s, %s, %s)"
            cursor = self.connection.cursor()
            cursor.execute(insert_query,value)
            cursor.execute(insert_query2,value)
            self.connection.commit()
            cursor.close()

    def get_all(self,table):
        select_query = f"SELECT * FROM {table}"
        cursor = self.connection.cursor()
        cursor.execute(select_query)
        return cursor.fetchall()

