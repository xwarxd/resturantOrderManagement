@app.route('/orders/<int:order_id>/toggle-payment', methods=['POST'])
def toggle_payment(order_id):
    session = Session()
    try:
        date = request.json.get('date')
        if not date:
            return jsonify({"error": "Date is required"}), 400

        order_date = datetime.strptime(date, '%Y-%m-%d').date()
        order = session.query(Order).filter(
            Order.order_id == order_id,
            func.date(Order.timestamp) == order_date
        ).first()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        order.paid = not order.paid
        session.commit()
        
        logging.info(f"Payment status toggled for order {order_id} on {date}. New status: {'Paid' if order.paid else 'Unpaid'}")
        return jsonify({"message": "Payment status toggled successfully", "paid": order.paid}), 200
    
    except Exception as e:
        logging.error(f"Error toggling payment status for order {order_id} on {date}: {str(e)}")
        session.rollback()
        return jsonify({"error": "An error occurred while toggling payment status"}), 500
    
    finally:
        session.close()

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    session = Session()
    try:
        date = request.json.get('date')
        if not date:
            return jsonify({"error": "Date is required"}), 400

        order_date = datetime.strptime(date, '%Y-%m-%d').date()
        order = session.query(Order).filter(
            Order.order_id == order_id,
            func.date(Order.timestamp) == order_date
        ).first()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        session.delete(order)
        session.commit()
        
        logging.info(f"Order {order_id} on {date} deleted successfully")
        return jsonify({"message": "Order deleted successfully"}), 200
    
    except Exception as e:
        logging.error(f"Error deleting order {order_id} on {date}: {str(e)}")
        session.rollback()
        return jsonify({"error": "An error occurred while deleting the order"}), 500
    
    finally:
        session.close()
