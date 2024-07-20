from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # This allows all origins

# Ensure the orders directory exists
if not os.path.exists('orders'):
    os.makedirs('orders')

@app.route('/menu', methods=['GET'])
def get_menu():
    return send_file('menu.json', mimetype='application/json')

@app.route('/order', methods=['POST'])
def place_order():
    order = request.json
    now = datetime.now()
    
    # Adjust the date if it's before 3 AM
    if now.hour < 3:
        order_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        order_date = now.strftime('%Y-%m-%d')
    
    date_file = f'orders/{order_date}.json'
    
    # Load existing orders or create a new list
    if os.path.exists(date_file):
        with open(date_file, 'r') as f:
            orders = json.load(f)
    else:
        orders = []

    # Generate a new order ID based on existing orders
    order_id = len(orders) + 1  # Start from 1 for each date
    
    # Calculate total for this order
    order_total = sum(item['price'] * item['quantity'] for item in order)
    
    order_data = {
        "order_id": order_id,
        "items": order,
        "timestamp": now.isoformat(),
        "total": order_total
    }
    orders.append(order_data)  # Append new order to the list

    # Save updated orders back to the file
    with open(date_file, 'w') as f:
        json.dump(orders, f, indent=2)

    return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    all_orders = []
    total_by_date = {}
    
    # List all files in the orders directory
    for filename in os.listdir('orders'):
        if filename.endswith('.json'):
            date = filename[:-5]  # Remove .json extension
            with open(f'orders/{filename}', 'r') as f:
                orders = json.load(f)
            
            # Calculate total for each order if not present
            for order in orders:
                if 'total' not in order:
                    order['total'] = sum(item['price'] * item['quantity'] for item in order['items'])
            
            daily_total = sum(order['total'] for order in orders)
            
            all_orders.extend(orders)
            total_by_date[date] = daily_total

    # Sort orders by timestamp
    all_orders.sort(key=lambda x: x['timestamp'], reverse=True)

    return jsonify({
        "orders": all_orders,
        "total_by_date": total_by_date
    })

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    date = request.json.get('date')
    if not date:
        return jsonify({"error": "Date is required"}), 400

    date_file = f'orders/{date}.json'
    
    if not os.path.exists(date_file):
        return jsonify({"error": "No orders found for this date"}), 404

    with open(date_file, 'r') as f:
        orders = json.load(f)

    # Find and remove the order
    orders = [order for order in orders if order['order_id'] != order_id]

    # Save updated orders back to the file
    with open(date_file, 'w') as f:
        json.dump(orders, f, indent=2)

    return jsonify({"message": "Order deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)