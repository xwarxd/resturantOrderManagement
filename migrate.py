from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://resturantdb_7hi6_user:zvNLfYmh2OpnAmelA5hzC9vh5uSDLmYo@dpg-cqduabhu0jms7391aj50-a.singapore-postgres.render.com/resturantdb_7hi6"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Order model with the new 'note' column
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    items = Column(String)
    timestamp = Column(DateTime)
    total = Column(Float)
    paid = Column(Boolean)
    note = Column(String(255))  # New column

def run_migration():
    # Create the new column
    with engine.connect() as connection:
        connection.execute('ALTER TABLE orders ADD COLUMN IF NOT EXISTS note VARCHAR(255)')
    
    print("Migration completed successfully. 'note' column added to 'orders' table.")

if __name__ == '__main__':
    run_migration()
