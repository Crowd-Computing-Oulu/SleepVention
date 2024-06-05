from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///database.db"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a base class for declarative class definitions
Base = declarative_base()

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
            Provides a database session for the application.

            This function yields a database session using the SessionLocal context manager.
            It ensures that the session is closed properly after its use.

            :yield: Database session.
        """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
