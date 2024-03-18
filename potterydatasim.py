import sqlite3
import numpy as np
from faker import Faker

# initialize Faker for generating simulated data
fake = Faker()

# define the path for the SQLite database
db_path = 'PotterySalesDB.db'

try:
# connect to the SQLite database, creating it if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"An error occurred connecting to the SQLite database: {e}")

try:
    # drop existing tables if they exist to start fresh
    cursor.execute('DROP TABLE IF EXISTS Product')
    cursor.execute('DROP TABLE IF EXISTS SalesTransaction')
    cursor.execute('DROP TABLE IF EXISTS Customer')
    cursor.execute('DROP TABLE IF EXISTS PurchaseItems')
    
    # create the Product table
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
    
     # create the Customers table
    cursor.execute('''
    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        CustomerName TEXT NOT NULL,
        CustomerLoc TEXT NOT NULL
    )
    ''')
    
    # create the SalesTransaction table
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
    
    # create the PurchaseItems table
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

# product details
product_types  = ['Vase', 'Mug', 'Bowl']
product_sizes  = ['Small','Medium','Large']
glazes         = ['Sangria', 'Autumn Purple', 'Kimchi', 'Cactus', 'Glacier', 'Pearl White'] # glazes from Spectrum Glazes 1430 Series - Cone 4/6 Floating Glazes
numproducts    = len(product_sizes)*len(product_types)*len(glazes)
print('numproducts', numproducts)
# price calculation function
def calculate_price(product_type, size):
    base_prices = {'Mug': 6.99, 'Vase': 20.99, 'Bowl': 12.99}
    size_increment = {'Mug': 3, 'Vase': 10, 'Bowl': 3}
    size_index = {'Small': 0, 'Medium': 1, 'Large': 2}
    price_increase = size_increment[product_type] * size_index[size]
    return base_prices[product_type] + price_increase

products_data = []
product_id = 1
product_ids = []
# generate all possible combinations of product type, glaze, and size
for product_type in product_types:
    for size in product_sizes:
        for glaze in glazes:
            name = f"{product_type} {glaze} {size}"
            price = calculate_price(product_type, size)
            products_data.append((product_id, name, product_type, size, glaze, price))
            product_ids.append(product_id)
            product_id += 1

try:
    cursor.executemany('INSERT INTO Product VALUES (?, ?, ?, ?, ?, ?)', products_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into Product table: {e}")

#------------- Customer details----------------------------------
num_customers   = 550
customer_data   = [(i, fake.name(), np.random.choice([fake.state(), 'North Carolina', 'North Carolina'])) # higher chance for sales in home state
                    for i in range(1, num_customers+1)]
try:
    cursor.executemany('INSERT INTO Customers VALUES (?, ?, ?)', customer_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into Customers table: {e}") 

#------------ Simulate SalesTransactions -------------------------
numtransactions = 614
sales_data      = []
months          = np.arange(1,13) 
# create transactions
for i in range(1, numtransactions+1):
    transaction_id = i
    if i <= num_customers:
        # use each customer at least once for the first 84 transactions
        customer_id = i
    else:
        # then randomly select from the existing customer IDs, allows repeat customers
        customer_id = np.random.randint(1,num_customers+1)
    num_prod_purchased = np.random.choice([1,2,3])
    # ItemsPurchased details
    purchaseitems_data = []
    for j in range(num_prod_purchased):
        product_id = np.random.randint(1,numproducts)
        purchaseitems_data.append((str(transaction_id)+"-"+str(j), product_id, [p[5] for p in products_data if p[0] == product_id][0], transaction_id))
    try:
        cursor.executemany('INSERT INTO PurchaseItems VALUES ( ?, ?, ?, ?)', purchaseitems_data)
    except sqlite3.Error as e:
        print(f"An error occurred inserting values into PurchaseItems table: {e}")
    total_price = np.sum([item[2] for item in purchaseitems_data])
    customer_state = customer_data[customer_id - 1][2]   # retrieve the state for the current customer_id from customer_data
    location       = np.random.choice(['online', 'farmers_market', 'pop_up']) if customer_state == 'North Carolina' else 'online'
    if location == 'farmers_market':
        prob_month = np.array([1.,1.,4.,5.,5.,4.,2.,1.,4.,5.,6.,9.]) # higher chance for xmas, lower chance for cold/hot weather
        prob_month /= prob_month.sum()                   # normalize
        month = np.random.choice(months,p=prob_month)
    else:
        prob_month = np.array([3.,4.,4.,4.,4.,4.,4.,4.,4.,4.,5.,8.]) # higher chance for xmas
        prob_month /= prob_month.sum()                   # normalize
        month = str(np.random.choice(months,p=prob_month)).zfill(2)
    day   = str(np.random.randint(1, 28)).zfill(2)
    year  = "2023"
    date  = f"{year}-{month}-{day}"
    sales_data.append((transaction_id, customer_id, total_price, date, location))
try:
    cursor.executemany('INSERT INTO SalesTransaction VALUES ( ?, ?, ?, ?, ?)', sales_data)
except sqlite3.Error as e:
    print(f"An error occurred inserting values into SalesTransaction table: {e}")

# commit changes and close the database connection
try:
    conn.commit()
except sqlite3.Error as e:
    print(f"An error occurred committing the transaction: {e}")
finally:
    conn.close()

print("PotterySalesDB database has been created and populated with simulated data.")

