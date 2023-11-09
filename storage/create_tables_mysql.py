import mysql.connector

db_conn = mysql.connector.connect(host="kakfa.eastus2.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE inventory_item
          (id INT NOT NULL AUTO_INCREMENT,
           product_id VARCHAR(250) NOT NULL,
           SKU VARCHAR(250) NOT NULL,
           product_name VARCHAR(1000) NOT NULL,
           compatibility VARCHAR(1000) NOT NULL,
           price INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           CONSTRAINT inventory_item_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE standard_order
          (id INT NOT NULL AUTO_INCREMENT, 
           order_id VARCHAR(250) NOT NULL,
           customer_name VARCHAR(250) NOT NULL,
           product_name VARCHAR(250) NOT NULL,
           shipping_address VARCHAR(250) NOT NULL,
           total_amount INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           CONSTRAINT standard_order_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()

