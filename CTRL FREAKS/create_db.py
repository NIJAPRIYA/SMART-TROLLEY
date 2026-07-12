import sqlite3

# Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('barcode_data.db')
c = conn.cursor()

# Create a table for products with 12-digit and 16-digit barcodes
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_price REAL NOT NULL,
    barcode_12_digits TEXT,
    barcode_16_digits TEXT
)
''')

# Insert sample data into the products table
sample_data = [
    ('Product A', 10.99, '123456789012', '1234567890123456'),
    ('Product B', 15.50, '234567890123', '2345678901234567'),
    ('Product C', 20.75, '345678901234', '3456789012345678')
]

c.executemany('''
    INSERT INTO products (product_name, product_price, barcode_12_digits, barcode_16_digits) 
    VALUES (?, ?, ?, ?)
''', sample_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully, and sample data inserted.")