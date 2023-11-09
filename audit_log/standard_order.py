from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class StandardOrder(Base):
    """ Blood Pressure """

    __tablename__ = "standard_order"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)
    customer_name = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    product_name = Column(String(250), nullable=False)
    shipping_address = Column(String(250), nullable=False)
    total_amount = Column(Integer, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, order_id, customer_name, timestamp, product_name, shipping_address, total_amount, trace_id):
        """ Initializes a blood pressure reading """
        self.order_id = order_id
        self.customer_name = customer_name
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.product_name = product_name
        self.shipping_address = shipping_address
        self.total_amount = total_amount
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['order_id'] = self.order_id
        dict['customer_name'] = self.customer_name
        dict['product_name'] = self.product_name
        dict['shipping_address'] = self.shipping_address
        dict['total_amount'] = self.total_amount
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
