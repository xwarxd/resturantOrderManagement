from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pytz
import json
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = "postgresql://resturantdb_7hi6_user:zvNLfYmh2OpnAmelA5hzC9vh5uSDLmYo@dpg-cqduabhu0jms7391aj50-a.singapore-postgres.render.com/resturantdb_7hi6"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Order model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    items = Column(String)
    timestamp = Column(DateTime)
    total = Column(Float)
    paid = Column(Boolean)

# Create the table
Base.metadata.create_all(engine)

# Helper function to get current time in IST
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

@app.route('/menu', methods=['GET'])
def get_menu():
    return send_file('menu.json', mimetype='application/json')

@app.route('/order', methods=['POST'])
def place_order():
    order_items = request.json
    now = get_ist_time()
    
    # Adjust the date if it's before 3 AM IST
    if now.hour < 3:
        order_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        order_date = now.strftime('%Y-%m-%d')
    
    session = Session()
    
    # Get the latest order_id for the current date
    latest_order = session.query(Order).filter(Order.timestamp >= order_date).order_by(Order.order_id.desc()).first()
    if latest_order:
        order_id = latest_order.order_id + 1
    else:
        order_id = 1
    
    # Calculate total for this order
    order_total = sum(item['price'] * item['quantity'] for item in order_items)
    
    new_order = Order(
        order_id=order_id,
        items=json.dumps(order_items),
        timestamp=now,
        total=order_total,
        paid=False
    )
    
    session.add(new_order)
    session.commit()
    session.close()
    
    return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    session = Session()
    orders = session.query(Order).order_by(Order.timestamp.desc()).all()
    
    all_orders = []
    total_by_date = {}
    
    for order in orders:
        order_dict = {
            "order_id": order.order_id,
            "items": json.loads(order.items),
            "timestamp": order.timestamp.isoformat(),
            "total": order.total,
            "paid": order.paid
        }
        all_orders.append(order_dict)
        
        date = order.timestamp.strftime('%Y-%m-%d')
        total_by_date[date] = total_by_date.get(date, 0) + order.total
    
    session.close()
    
    return jsonify({
        "orders": all_orders,
        "total_by_date": total_by_date
    })

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    date = request.json.get('date')
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    session = Session()
    order = session.query(Order).filter(Order.order_id == order_id, Order.timestamp >= date).first()
    
    if not order:
        session.close()
        return jsonify({"error": "Order not found"}), 404
    
    session.delete(order)
    session.commit()
    session.close()
    
    return jsonify({"message": "Order deleted successfully"}), 200

@app.route('/orders/<int:order_id>/toggle-payment', methods=['POST'])
def toggle_payment(order_id):
    date = request.json.get('date')
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    session = Session()
    order = session.query(Order).filter(Order.order_id == order_id, Order.timestamp >= date).first()
    
    if not order:
        session.close()
        return jsonify({"error": "Order not found"}), 404
    
    order.paid = not order.paid
    session.commit()
    session.close()
    
    return jsonify({"message": "Payment status toggled successfully", "paid": order.paid}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
