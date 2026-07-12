from flask import Flask, request, jsonify, render_template, session
import sqlite3
import qrcode
from io import BytesIO
import base64
import pandas as pd
import datetime
import joblib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------------------
# Load discount prediction model
# ------------------------------
MODEL_PATH = r"C:\Yaazh\MyProjects\CTRL FREAKS\discount_model11.pkl"
PURCHASE_CSV = "purchased_products.csv"
DISCOUNT_CSV = "products_discount_output.csv"

discount_model = None
try:
    discount_model = joblib.load(MODEL_PATH)
    print("✅ Discount model loaded successfully.")
except Exception as e:
    print("⚠️ Failed to load discount model:", e)

# ------------------------------
# Database: fetch product info
# ------------------------------
def check_product(barcode, barcode_type='12'):
    conn = sqlite3.connect('barcode_data.db')
    c = conn.cursor()
    if barcode_type == '12':
        c.execute("SELECT product_name, product_price FROM products WHERE barcode_12_digits = ?", (barcode,))
    else:
        c.execute("SELECT product_name, product_price FROM products WHERE barcode_16_digits = ?", (barcode,))
    result = c.fetchone()
    conn.close()
    return result

# ------------------------------
# Initialize session
# ------------------------------
@app.before_request
def initialize_cart():
    if 'cart' not in session:
        session['cart'] = {}

# ------------------------------
# Home page
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------------------
# Add/remove product from cart
# ------------------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    barcode_16 = data.get('barcode_16_digits', '')
    barcode_12 = barcode_16[:12]

    if not barcode_16:
        return jsonify({"success": False, "error": "No barcode provided."}), 400

    product_info = check_product(barcode_12, '12')
    if product_info:
        product_name, product_price = product_info

        if barcode_16 in session['cart']:
            del session['cart'][barcode_16]
            session.modified = True
            message = f"Product {product_name} removed from cart."
        else:
            session['cart'][barcode_16] = {"name": product_name, "price": product_price, "quantity": 1}
            session.modified = True
            message = f"Product {product_name} added to cart."

        return jsonify({"success": True, "message": message, "price": product_price}), 200

    return jsonify({"success": False, "error": "No valid barcode found."}), 400

# ------------------------------
# Generate QR & Save purchase + discounts
# ------------------------------
@app.route('/generate_qr_code', methods=['POST'])
def generate_qr_code():
    data = request.form
    amount = data.get('amount')
    upi_id = '9342447865@ptyes'
    name = 'YAAZHINI S'

    if not amount:
        return jsonify({"success": False, "message": "No amount provided."}), 400

    # Generate QR
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    qr = qrcode.make(upi_url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_code_url = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # ✅ Save purchase details to CSV
    save_purchase_details(session['cart'])

    # Clear cart after purchase
    session['cart'] = {}
    session.modified = True

    return jsonify({"success": True, "qr_code_url": f"data:image/png;base64,{qr_code_url}", "upi_url": upi_url})

# ------------------------------
# Save purchase details to CSV
# ------------------------------
def save_purchase_details(cart):
    if not cart:
        print("⚠️ No purchased products found yet! Buy products first.")
        return

    today = datetime.date.today()
    data = []

    for barcode, item in cart.items():
        data.append({
            "Product_Name": item["name"],
            "Quantity": item["quantity"],
            "Total_Price": float(item["price"]) * item["quantity"],
            "Purchase_Date": today.strftime("%Y-%m-%d")
        })

    new_df = pd.DataFrame(data)

    # Append or create CSV
    if os.path.exists(PURCHASE_CSV):
        purchase_df = pd.read_csv(PURCHASE_CSV)
        purchase_df = pd.concat([purchase_df, new_df], ignore_index=True)
    else:
        purchase_df = new_df

    purchase_df.to_csv(PURCHASE_CSV, index=False)
    print("🛒 Purchase details saved successfully.")

    # Update discount predictions
    update_discount_predictions(purchase_df)

# ------------------------------
# Predict & update discounts
# ------------------------------
def update_discount_predictions(purchase_df):
    if discount_model is None:
        print("⚠️ Discount model not loaded. Skipping predictions.")
        return

    # Aggregate product-level info
    product_summary = purchase_df.groupby("Product_Name").agg({
        "Quantity": "sum",
        "Total_Price": "sum",
        "Purchase_Date": "max"
    }).reset_index()

    # Ensure date type
    product_summary["Purchase_Date"] = pd.to_datetime(product_summary["Purchase_Date"], errors='coerce')

    # Calculate days since last purchase safely
    product_summary["Days_Since_Purchase"] = (
        datetime.date.today() - product_summary["Purchase_Date"].dt.date
    ).apply(lambda x: x.days if pd.notnull(x) else 0)

    # Predict discount
    try:
        X = product_summary[["Quantity", "Total_Price", "Days_Since_Purchase"]]
        product_summary["Predicted_Discount"] = discount_model.predict(X)
    except Exception as e:
        print("⚠️ Model prediction failed:", e)
        product_summary["Predicted_Discount"] = 0

    # Update main discount CSV (overwrite with merged data)
    if os.path.exists(DISCOUNT_CSV):
        existing = pd.read_csv(DISCOUNT_CSV)
        merged = pd.concat([existing, product_summary], ignore_index=True)
    else:
        merged = product_summary

    # Keep latest per product
    merged.drop_duplicates(subset=["Product_Name"], keep="last", inplace=True)
    merged.to_csv(DISCOUNT_CSV, index=False)
    print("✅ Discount predictions updated successfully.")

# ------------------------------
# Clear cart route
# ------------------------------
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return jsonify({"success": True, "message": "Cart cleared successfully."})

# ------------------------------
# Run Flask app
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
