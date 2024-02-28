import sqlite3
import numpy as np
from faker import Faker

# Initialize Faker for generating simulated data
fake = Faker()

# Define the path for the SQLite database
db_path = 'PotterySalesDB.db'

# Connect to the SQLite database, creating it if it doesn't exist
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop existing tables if they exist to start fresh
cursor.execute('DROP TABLE IF EXISTS Product')
cursor.execute('DROP TABLE IF EXISTS SalesTransaction')
cursor.execute('DROP TABLE IF EXISTS Customer')

# Create the Product table
cursor.execute('''
CREATE TABLE Product (
    ProductID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Type TEXT NOT NULL,
    Size TEXT NOT NULL,
    Glaze TEXT NOT NULL,
    Price REAL NOT NULL
)
''')

# Create the SalesTransaction table
cursor.execute('''
CREATE TABLE SalesTransaction (
    TransactionID INTEGER PRIMARY KEY,
    ProductID INTEGER NOT NULL,
    Price INTEGER NOT NULL,
    PurchaseDate TEXT NOT NULL,
    Location TEXT NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
)
''')


# Product details
product_types = ['Vase', 'Mug', 'Bowl']
glazes = ['Sangria', 'Autumn Purple', 'Kimchi', 'Cactus', 'Glacier', 'Pearl White'] #glazes from Spectrum Glazes 1430 Series - Cone 4/6 Floating Glazes
products_data = [(i, f"{(product_type := np.random.choice(product_types))} {(glaze := np.random.choice(glazes))}", product_type,
                  np.random.choice(['Small', 'Medium', 'Large']), glaze, round(np.random.randint(20, 100)+np.random.choice([0.0,0.50,0.99]),2))
                 for i in range(1, 101)]
cursor.executemany('INSERT INTO Product VALUES (?, ?, ?, ?, ?, ?)', products_data)

# Simulate SalesTransactions
sales_data = []
for i in range(1, 101):
    month =  str(np.random.randint(1, 13)).zfill(2)
    day = str(np.random.randint(1, 28)).zfill(2)
    year = "2023"
    date = f"{year}-{month}-{day}"
    location = np.random.choice(['online', 'farmers_market', 'pop_up'])
    product_id = np.random.randint(1, 101)
    price = [p[5] for p in products_data if p[0] == product_id][0]
    sales_data.append((i, product_id, price, date, location))

cursor.executemany('INSERT INTO SalesTransaction VALUES ( ?, ?, ?, ?, ?)', sales_data)

# Commit changes and close the database connection
conn.commit()
conn.close()

print("PotterySalesDB database has been created and populated with simulated data.")

