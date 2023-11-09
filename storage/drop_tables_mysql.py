import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-fall2023.eastus2.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          DROP TABLE blood_pressure, heart_rate
          ''')

db_conn.commit()
db_conn.close()
