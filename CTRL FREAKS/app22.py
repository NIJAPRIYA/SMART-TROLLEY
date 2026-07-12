from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

CSV_FILE = os.path.join(os.path.dirname(__file__), "products_discount_output.csv")

@app.route('/')
def index():
    try:
        purchase_data = pd.read_csv(CSV_FILE)

        # Bar Chart - Total sales per product
        bar_fig = px.bar(
            purchase_data,
            x='Product_Name',
            y='Total_Price',
            title="Total Revenue per Product",
            text='Total_Price',
            labels={'Product_Name': 'Product', 'Total_Price': 'Revenue (Rs.)'},
            color='Total_Price',
            color_continuous_scale='Viridis'
        )
        bar_fig.update_traces(texttemplate='Rs.%{text:.2f}', textposition='outside')

        # Donut Chart - Contribution % of each product
        donut_fig = px.pie(
            purchase_data,
            names='Product_Name',
            values='Total_Price',
            title='Revenue Contribution by Product',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        donut_fig.update_traces(textinfo='percent+label')

        bar_html = pio.to_html(bar_fig, full_html=False)
        donut_html = pio.to_html(donut_fig, full_html=False)

        return render_template("index22.html", bar_chart=bar_html, donut_chart=donut_html)

    except FileNotFoundError:
        return "<h2>No purchased products found yet! Buy products first.</h2>"

if __name__ == '__main__':
    app.run(debug=True, port=5005)
