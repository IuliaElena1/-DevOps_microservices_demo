import os
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine(
    "mysql+pymysql://{user}:{pw}@{host}:{port}/{db}".format(
        user=os.getenv("DB_USER", "app_user"),
        pw=os.getenv("DB_PASSWORD", "userpassword123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "3306"),
        db=os.getenv("DB_NAME", "number_inventory"),
    )
)


class Base(DeclarativeBase):
    pass


class PhoneNumberRow(Base):
    __tablename__ = "numbers"

    id              = Column(Integer,      primary_key=True, autoincrement=True)
    e164            = Column(String(20),   unique=True, nullable=False, index=True)
    country_code    = Column(String(5),    nullable=False)
    status          = Column(String(20),   nullable=False, default="AVAILABLE")
    customer_id     = Column(Integer,      nullable=True)
    current_carrier = Column(String(100),  nullable=False)
    signature       = Column(String(500),  nullable=True)
    version         = Column(Integer,      nullable=False, default=1)


def create_tables():
    Base.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
