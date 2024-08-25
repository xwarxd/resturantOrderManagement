from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pytz
import json
import logging
import random
import string

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database configuration
DATABASE_URL = "postgresql://resturantdb_bca1_user:w0YDkOAEGvyhTVKh4FfiRauHP3eHK9Ca@dpg-cr5f7d88fa8c73ae8c90-a.singapore-postgres.render.com/resturantdb_bca1"
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
    note = Column(String(255))
    unqID = Column(String(10), unique=True)  # New column

# Create the table
Base.metadata.create_all(engine)

# Helper function to get current time in IST
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

# Helper function to generate unique ID
def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@app.route('/menu', methods=['GET'])
def get_menu():
    return send_file('menu.json', mimetype='application/json')

@app.route('/order', methods=['POST'])
def place_order():
    order_data = request.json
    order_items = order_data['items']
    note = order_data.get('note', '')
    now = get_ist_time()
    
    if now.hour < 3:
        order_date = (now - timedelta(days=1)).date()
    else:
        order_date = now.date()
    
    session = Session()
    try:
        highest_order = session.query(func.max(Order.order_id)).filter(
            func.date(Order.timestamp) == order_date
        ).scalar()
        
        order_id = highest_order + 1 if highest_order is not None else 1
        
        order_total = sum(item['price'] * item['quantity'] for item in order_items)
        
        new_order = Order(
            order_id=order_id,
            items=json.dumps(order_items),
            timestamp=now,
            total=order_total,
            paid=False,
            note=note,
            unqID=generate_unique_id()  # Generate and assign unique ID
        )
        
        session.add(new_order)
        session.commit()
        
        logging.info(f"New order placed with order_id: {order_id}, unqID: {new_order.unqID}")
        return jsonify({"message": "Order placed successfully", "order_id": order_id, "unqID": new_order.unqID}), 201
    
    except Exception as e:
        logging.error(f"Error placing order: {str(e)}")
        session.rollback()
        return jsonify({"error": "An error occurred while placing the order"}), 500
    
    finally:
        session.close()

@app.route('/orders', methods=['GET'])
def get_orders():
    session = Session()
    try:
        orders = session.query(Order).order_by(Order.timestamp.desc()).all()
        
        all_orders = []
        total_by_date = {}
        
        for order in orders:
            order_dict = {
                "order_id": order.order_id,
                "items": json.loads(order.items),
                "timestamp": order.timestamp.isoformat(),
                "total": order.total,
                "paid": order.paid,
                "note": order.note,
                "unqID": order.unqID  # Include the unique ID in the response
            }
            all_orders.append(order_dict)
            
            date = order.timestamp.strftime('%Y-%m-%d')
            total_by_date[date] = total_by_date.get(date, 0) + order.total
        
        logging.info("Orders retrieved successfully")
        return jsonify({
            "orders": all_orders,
            "total_by_date": total_by_date
        })
    
    except Exception as e:
        logging.error(f"Error retrieving orders: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving orders"}), 500
    
    finally:
        session.close()

@app.route('/orders/<string:unq_id>', methods=['DELETE'])
def delete_order(unq_id):
    session = Session()
    try:
        order = session.query(Order).filter(Order.unqID == unq_id).first()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        session.delete(order)
        session.commit()
        
        logging.info(f"Order with unqID {unq_id} deleted successfully")
        return jsonify({"message": "Order deleted successfully"}), 200
    
    except Exception as e:
        logging.error(f"Error deleting order with unqID {unq_id}: {str(e)}")
        session.rollback()
        return jsonify({"error": "An error occurred while deleting the order"}), 500
    
    finally:
        session.close()

@app.route('/orders/<string:unq_id>/toggle-payment', methods=['POST'])
def toggle_payment(unq_id):
    session = Session()
    try:
        order = session.query(Order).filter(Order.unqID == unq_id).first()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        order.paid = not order.paid
        session.commit()
        
        logging.info(f"Payment status toggled for order with unqID {unq_id}. New status: {'Paid' if order.paid else 'Unpaid'}")
        return jsonify({"message": "Payment status toggled successfully", "paid": order.paid}), 200
    
    except Exception as e:
        logging.error(f"Error toggling payment status for order with unqID {unq_id}: {str(e)}")
        session.rollback()
        return jsonify({"error": "An error occurred while toggling payment status"}), 500
    
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
