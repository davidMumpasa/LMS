import mysql.connector


def get_connection():
    # Replace the placeholders with your MySQL server details
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Fifimbula@10',
        database='lms'
    )
    return connection


def close_connection(connection):
    connection.close()
