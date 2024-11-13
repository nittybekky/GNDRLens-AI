from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Set the database URL (you can use an environment variable for production purposes)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safespace.db")

# Create an engine to connect to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session local instance for DB interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for your models (ensure all models inherit from this)
Base = declarative_base()

# Dependency to get the database session in the route handlers
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables
def create_tables():
    # Ensure all models are imported so their tables are registered
    from app.models import user, analysis  # Import the models here to ensure they're registered
    try:
        Base.metadata.create_all(bind=engine)  # Create all tables
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
