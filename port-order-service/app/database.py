import os
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine(
    "mysql+pymysql://{user}:{pw}@{host}:{port}/{db}".format(
        user=os.getenv("DB_USER", "app_user"),
        pw=os.getenv("DB_PASSWORD", "userpassword123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "3306"),
        db=os.getenv("DB_NAME", "port_order"),
    )
)


class Base(DeclarativeBase):
    pass


class PortOrderRow(Base):
    __tablename__ = "port_orders"

    e164           = Column(String(20),  primary_key=True)
    customer_id    = Column(Integer,     nullable=True)
    status         = Column(String(30),  nullable=False, default="AVAILABLE")
    next_action_at = Column(DateTime(timezone=True), nullable=True)
    version        = Column(Integer,     nullable=False, default=0)


def create_tables():
    Base.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
