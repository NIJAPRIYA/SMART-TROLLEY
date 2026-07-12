import sqlite3

# Function to connect to the database
def connect_to_db():
    return sqlite3.connect('barcode_data.db')

# Function to setup the cart table
def setup_cart_table():
    conn = connect_to_db()
    c = conn.cursor()

    # Create the cart table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            product_name TEXT,
            barcode_16_digits TEXT UNIQUE,
            price REAL,
            quantity INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# Function to add a product to the cart or update if already in the cart
def add_product_to_cart(product_name, barcode_16_digits, product_price, quantity=1):
    conn = connect_to_db()
    c = conn.cursor()

    # Check if the product is already in the cart
    c.execute('SELECT quantity FROM cart WHERE barcode_16_digits = ?', (barcode_16_digits,))
    result = c.fetchone()

    if result:
        # If the product is already in the cart, update the quantity
        new_quantity = result[0] + quantity
        c.execute('''
            UPDATE cart SET quantity = ?, price = price + ? WHERE barcode_16_digits = ?
        ''', (new_quantity, product_price, barcode_16_digits))
        print(f"Updated {product_name}: new quantity is {new_quantity}")
    else:
        # If the product is not in the cart, add it
        c.execute('''
            INSERT INTO cart (product_name, barcode_16_digits, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (product_name, barcode_16_digits, product_price, quantity))
        print(f"Added {product_name} to cart.")

    conn.commit()
    conn.close()

# Function to remove a product from the cart or reduce its quantity
def remove_product_from_cart(product_name, barcode_16_digits, product_price, quantity=1):
    conn = connect_to_db()
    c = conn.cursor()

    # Check if the product is in the cart
    c.execute('SELECT quantity FROM cart WHERE barcode_16_digits = ?', (barcode_16_digits,))
    result = c.fetchone()

    if result:
        current_quantity = result[0]

        if current_quantity > quantity:
            # Reduce the quantity if more than the requested removal amount
            new_quantity = current_quantity - quantity
            c.execute('''
                UPDATE cart SET quantity = ?, price = price - ? WHERE barcode_16_digits = ?
            ''', (new_quantity, product_price, barcode_16_digits))
            print(f"Removed {quantity} of {product_name}. Remaining quantity is {new_quantity}.")
        else:
            # Remove the product if quantity reaches 0
            c.execute('DELETE FROM cart WHERE barcode_16_digits = ?', (barcode_16_digits,))
            print(f"Removed {product_name} from cart.")

    else:
        print(f"{product_name} not found in the cart.")

    conn.commit()
    conn.close()

# Function to display the current cart with total price
def display_cart():
    conn = connect_to_db()
    c = conn.cursor()

    c.execute('SELECT product_name, price, quantity FROM cart')
    cart_items = c.fetchall()

    if cart_items:
        total_price = 0
        print("\nCurrent items in the cart:")
        print(f"{'Product Name':<20} {'Price':<10} {'Quantity':<10}")
        print("-" * 40)
        
        for item in cart_items:
            product_name, price, quantity = item
            total_price += price  # Summing up the total price

            print(f"{product_name:<20} {price:<10.2f} {quantity:<10}")

        print("-" * 40)
        print(f"Total Price: {total_price:.2f}")
    else:
        print("The cart is empty.")

    conn.close()

# Main function to manage the cart
def manage_cart(barcode_16_digits):
    # Check if the barcode is exactly 16 digits long
    if len(barcode_16_digits) != 16:
        print("Invalid entry: Barcode must be 16 digits long.")
        return  # Exit the function if the barcode length is incorrect

    conn = connect_to_db()
    c = conn.cursor()

    # Extract the first 12 digits of the barcode to find the product
    product_code = barcode_16_digits[:12]

    # Look up the product in the products table by its 12-digit barcode
    c.execute('SELECT product_name, product_price FROM products WHERE barcode_12_digits = ?', (product_code,))
    product_info = c.fetchone()

    if product_info:
        product_name, product_price = product_info

        # Check if the product is already in the cart
        c.execute('SELECT quantity FROM cart WHERE barcode_16_digits = ?', (barcode_16_digits,))
        cart_info = c.fetchone()

        if cart_info:
            # If the product is already in the cart, remove it
            remove_product_from_cart(product_name, barcode_16_digits, product_price)
        else:
            # Otherwise, add the product to the cart
            add_product_to_cart(product_name, barcode_16_digits, product_price)

        # Display updated cart after operation
        display_cart()
    else:
        print("Product not found in the database.")

    conn.close()  # Close the connection after all operations

# Initialize the database and cart table
setup_cart_table()

# Clear the cart if requested
clear_cart = input("Do you want to clear the cart? (yes/no): ").strip().lower()

if clear_cart == 'yes':
    conn = connect_to_db()
    c = conn.cursor()
    c.execute('DELETE FROM cart')
    conn.commit()
    conn.close()
    print("The cart has been cleared.")

# Ask for the barcode input and manage the cart
barcode_16_digits = input("Enter the full 16 digits of the barcode: ").strip()
manage_cart(barcode_16_digits)