from app.infrastructure.database.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, text


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    ordered_at = Column(DateTime, server_default=text("NOW()"))
