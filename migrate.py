from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string

# Database configuration
DATABASE_URL = "postgresql://joncafe_user:RVPCMqsw8Y0PUyKyIFSLdPV28a277bSw@dpg-crpv3vt6l47c73aqkf80-a/joncafe"
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
    unqID = Column(String(10), unique=True)  # Kept as unqID

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def run_migration():
    # Create the new column with exact case
    with engine.connect() as connection:
        connection.execute('ALTER TABLE orders ADD COLUMN IF NOT EXISTS "unqID" VARCHAR(10) UNIQUE')
    
    # Generate and set unique IDs for existing orders
    session = Session()
    try:
        orders = session.query(Order).all()
        for order in orders:
            if not order.unqID:
                order.unqID = generate_unique_id()
        session.commit()
        print("Migration completed successfully. 'unqID' column added to 'orders' table and existing orders updated.")
    except Exception as e:
        session.rollback()
        print(f"Error during migration: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    run_migration()
