from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True, # Verify connections before using them
    echo=False # Set to True to see raw SQL logs
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)