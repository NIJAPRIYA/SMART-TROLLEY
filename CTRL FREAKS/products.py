import barcode
from barcode.writer import ImageWriter
import os
import sqlite3
import random

# Define the output directory globally
output_dir = r"C:\Yaazh\MyProjects\CTRL FREAKS\static\barcodes"

# Function to set up the database
def setup_database():
    """Create the product table if it doesn't exist."""
    conn = sqlite3.connect(r"C:\Yaazh\MyProjects\CTRL FREAKS\barcode_data.db")
    c = conn.cursor()

    # Create a table for products if it doesn't already exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_price REAL NOT NULL,
            barcode_12_digits TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Function to check if the product is in the database
def check_product_in_db(product_name, product_price):
    """Check if a product with the given name and price exists in the database."""
    conn = sqlite3.connect(r"C:\Yaazh\MyProjects\CTRL FREAKS\barcode_data.db")
    
    c = conn.cursor()
    
    c.execute('''
        SELECT barcode_12_digits FROM products 
        WHERE product_name = ? AND product_price = ?
    ''', (product_name, product_price))
    
    result = c.fetchone()
    conn.close()

    if result:
        return result[0]  # Return the 12-digit barcode
    return None

# Function to save the product to the database
def save_product_to_db(product_name, product_price, barcode_12_digits):
    """Save a new product to the database."""
    conn = sqlite3.connect(r"C:\Yaazh\MyProjects\CTRL FREAKS\barcode_data.db")
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO products (product_name, product_price, barcode_12_digits)
        VALUES (?, ?, ?)
    ''', (product_name, product_price, barcode_12_digits))
    
    conn.commit()
    conn.close()

# Function to generate a random 12-digit code
def generate_random_12_digit_code():
    """Generate a random 12-digit number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])

# Function to generate barcodes and save them as images in a product-specific folder
def generate_barcodes_with_product_info(product_name, product_price, start_qty, count):
    """Generate barcodes with a randomly generated 12-digit number for the product."""

    # Create a subdirectory for the product within the output directory
    product_dir = os.path.join(output_dir, product_name)
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
    
    product_code = check_product_in_db(product_name, product_price)
    
    if product_code:
        print(f"Product already exists. Using existing 12-digit code: {product_code}")
    else:
        product_code = generate_random_12_digit_code()
        print(f"Generated new 12-digit code for {product_name} (Price: {product_price}): {product_code}")
        save_product_to_db(product_name, product_price, product_code)
    
    writer_options = {
        "module_height": 22.0,
        "font_size": 12,
        "text_distance": 5,
        "quiet_zone": 6.5,
        "module_width": 0.5
    }
    
    for i in range(count):
        current_qty = start_qty + i
        quantity = f"{current_qty:04d}"
        full_barcode = product_code + quantity
        
        try:
            code128 = barcode.get_barcode_class('code128')
            code128_barcode = code128(full_barcode, writer=ImageWriter())
            filename = os.path.join(product_dir, f"barcode_{product_name}_{full_barcode}.png")
            code128_barcode.save(filename, writer_options)
            print(f"Saved: {filename}")

        except Exception as e:
            print(f"Error generating barcode {full_barcode}: {e}")
