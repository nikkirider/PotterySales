import sqlite3
import numpy as np
from faker import Faker

# Initialize Faker for generating simulated data
fake = Faker()

# Define the path for the SQLite database
db_path = 'PotterySalesDB.db'

try:
# Connect to the SQLite database, creating it if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"An error occurred connecting to the SQLite database: {e}")

try:
    # Drop existing tables if they exist to start fresh
    cursor.execute('DROP TABLE IF EXISTS Product')
    cursor.execute('DROP TABLE IF EXISTS SalesTransaction')
    cursor.execute('DROP TABLE IF EXISTS Customer')
    cursor.execute('DROP TABLE IF EXISTS PurchaseItems')
    
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
    
     # Create the Customers table
    cursor.execute('''
    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        CustomerName TEXT NOT NULL,
        CustomerLoc TEXT NOT NULL
    )
    ''')
    
    # Create the SalesTransaction table
    cursor.execute('''
    CREATE TABLE SalesTransaction (
        TransactionID INTEGER PRIMARY KEY,
        CustomerID INTEGER NOT NULL,
        TotalPrice REAL NOT NULL,
        PurchaseDate TEXT NOT NULL,
        PurchaseLoc TEXT NOT NULL,
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
    )
    ''')
    
    # Create the PurchaseItems table
    cursor.execute('''
    CREATE TABLE PurchaseItems (
        PurchaseItemID TEXT PRIMARY KEY,
        ProductID INTEGER NOT NULL,
        ProductPrice REAL NOT NULL,
        TransactionID INTEGER NOT NULL,
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
        FOREIGN KEY (TransactionID) REFERENCES SalesTransaction(TransactionID)
    ) 
    ''')
except sqlite3.Error as e:
    print(f"An error occurred creating tables: {e}")

# Product details
numproducts    = 50
product_types  = ['Vase', 'Mug', 'Bowl']
glazes         = ['Sangria', 'Autumn Purple', 'Kimchi', 'Cactus', 'Glacier', 'Pearl White'] #glazes from Spectrum Glazes 1430 Series - Cone 4/6 Floating Glazes
products_data  = [(i, f"{(product_type := np.random.choice(product_types))} {(glaze := np.random.choice(glazes))}", product_type,
                   np.random.choice(['Small', 'Medium', 'Large']), glaze, round(np.random.randint(20, 100)+np.random.choice([0.0,0.50,0.99]),2))
                   for i in range(1, numproducts+1)]
try:
    cursor.executemany('INSERT INTO Product VALUES (?, ?, ?, ?, ?, ?)', products_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into Product table: {e}")

# Customer details
num_customers   = 84
customer_data   = [(i, fake.name(), fake.state())
                    for i in range(1, num_customers+1)]
try:
    cursor.executemany('INSERT INTO Customers VALUES (?, ?, ?)', customer_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into Customers table: {e}") 

# Simulate SalesTransactions
numtransactions = 100
sales_data      = []
for i in range(1, numtransactions+1):
    transaction_id = i
    if i <= num_customers:
        # Use each customer at least once for the first 84 transactions
        customer_id = i
    else:
        # For transactions 85-100, randomly select from the existing customer IDs
        customer_id = np.random.randint(1,num_customers+1)
    num_prod_purchased = np.random.choice([1,2,3])
    # ItemsPurchased details
    purchaseitems_data = []
    purchaseitems_data = [(str(transaction_id)+"-"+str(j), product_id := np.random.randint(1, numproducts+1), price :=  [p[5] for p in products_data if p[0] == product_id][0], transaction_id)
                          for j in range(num_prod_purchased)]
    try:
        cursor.executemany('INSERT INTO PurchaseItems VALUES ( ?, ?, ?, ?)', purchaseitems_data)
    except sqlite3.Error as e:
        print(f"An error occurred inserting values into PurchaseItems table: {e}")
    total_price = np.sum([item[2] for item in purchaseitems_data])
    month =  str(np.random.randint(1, 13)).zfill(2)
    day   = str(np.random.randint(1, 28)).zfill(2)
    year  = "2023"
    date  = f"{year}-{month}-{day}"
    customer_state = customer_data[customer_id - 1][2] # Retrieve the state for the current customer_id from customer_data
    location       = np.random.choice(['online', 'farmers_market', 'pop_up']) if customer_state == 'North Carolina' else 'online'
    sales_data.append((transaction_id, customer_id, total_price, date, location))
try:
    cursor.executemany('INSERT INTO SalesTransaction VALUES ( ?, ?, ?, ?, ?)', sales_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into SalesTransaction table: {e}")

# Commit changes and close the database connection
try:
    conn.commit()
except sqlite3.Error as e:
    print(f"An error occurred committing the transaction: {e}")
finally:
    conn.close()

print("PotterySalesDB database has been created and populated with simulated data.")

