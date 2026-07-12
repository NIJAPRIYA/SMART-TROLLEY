from flask import Flask, render_template, request, jsonify
from products import generate_barcodes_with_product_info, setup_database

app = Flask(__name__, static_folder='static')  # Ensure Flask knows the static folder

# Initialize the database when the app starts
setup_database()

@app.route('/')
def index():
    return render_template('index11.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get data from the JSON body
        data = request.form  # Using form data for the form submission
        product_name = data['product_name']
        product_price = float(data['product_price'])
        product_start = int(data['product_start'])
        product_quan = int(data['product_quan'])

        # Generate barcodes using the function from products.py
        generate_barcodes_with_product_info(product_name, product_price, product_start, product_quan)

        # Respond with a success message
        return jsonify({"message": f"Barcodes for {product_name} generated successfully!"})

    except Exception as e:
        # Handle errors and return a failure message
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Running on port 5002
