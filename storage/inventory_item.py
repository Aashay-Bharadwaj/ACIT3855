from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class InventoryItem(Base):
    """ Blood Pressure """

    __tablename__ = "inventory_item"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(250), nullable=False)
    SKU = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    product_name = Column(String(1000), nullable=False)
    compatibility = Column(String(1000), nullable=False)
    price = Column(Integer, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, product_id, SKU, timestamp, product_name, compatibility, price, trace_id):
        """ Initializes a blood pressure reading """
        self.product_id = product_id
        self.SKU = SKU
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.product_name = product_name
        self.compatibility = compatibility
        self.price = price
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['product_id'] = self.product_id
        dict['SKU'] = self.SKU
        dict['product_name'] = self.product_name
        dict['compatibility'] = self.compatibility
        dict['price'] = self.price
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
