from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://resturantdb_7hi6_user:zvNLfYmh2OpnAmelA5hzC9vh5uSDLmYo@dpg-cqduabhu0jms7391aj50-a.singapore-postgres.render.com/resturantdb_7hi6"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Order(db.Model):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    items = Column(String)
    timestamp = Column(DateTime)
    total = Column(Float)
    paid = Column(Boolean)
    note = Column(String(255))  # New column for the note

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Database tables created. You can now run the migration commands.")
