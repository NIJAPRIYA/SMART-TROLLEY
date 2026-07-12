from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Path to the CSV file
csv_file_path = r"C:/Users/DELL/Desktop/TROLLEYYYY/product_discounts_output.csv"

@app.route('/')
def index():
    # Read the product data from the CSV file
    purchase_data = pd.read_csv(csv_file_path)

    # Filter the necessary columns for the chart: Product Name and Discount
    chart_data = purchase_data[['Product_Name', 'Predicted_Discount']]
    
        # Log current session cart after modification
        print(f"Current cart after modification: {session.get('cart', {})}")
        return jsonify({"success": True, "message": message, "price": product_price}), 200

    print("No valid barcode found in the database.")
    return jsonify({"success": False, "error": "No valid barcode found."}), 400
    

    # Convert the Plotly figure to HTML
    graph_html = pio.to_html(fig, full_html=False)

    # Render the HTML template and pass the chart
    return render_template("index22.html", graph_html=graph_html)

if __name__ == '__main__':
    # Run Flask on port 5002
    app.run(debug=True, port=5005)
