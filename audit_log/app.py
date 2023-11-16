import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from inventory_item import InventoryItem
from standard_order import StandardOrder
from flask_cors import CORS, cross_origin
# from apscheduler.schedulers.background import BackgroundScheduler
import yaml
import logging
import logging.config

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:'
    f'{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:'
    f'{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def report_inventory_item(body):
    """ Receives a blood pressure reading """

    session = DB_SESSION()

    item = InventoryItem(body['product_id'],
                       body['SKU'],
                       body['timestamp'],
                       body['product_name'],
                       body['compatibility'],
                       body['price'],
                       body['trace_id'])

    session.add(item)

    session.commit()
    session.close()

    logger.debug("Stored event Blood Pressure request with a unique id of %s and trace id of %s" %
                 (body["SKU"], body["trace_id"]))

    return NoContent, 201


def report_standard_order(body):
    """ Receives a heart rate (pulse) reading """

    session = DB_SESSION()

    order = StandardOrder(body['order_id'],
                   body['customer_name'],
                   body['timestamp'],
                   body['product_name'],
                   body['shipping_address'],
                   body['total_amount'],
                   body['trace_id'])

    session.add(order)

    session.commit()
    session.close()

    logger.debug("Stored event Heart Rate request with a unique id of %s and trace id of %s" %
                 (body["order_id"], body["trace_id"]))

    return NoContent, 201


def get_inventory_item(index):
    # """ Gets new blood pressure readings after the timestamp """

    # session = DB_SESSION()

    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    # readings = session.query(InventoryItem).filter(InventoryItem.date_created >=
    #                                                timestamp_datetime)

    # results_list = []

    # for reading in readings:
    #     results_list.append(reading.to_dict())

    # session.close()

    # logger.info("Query for Blood Pressure readings after %s returns %d results" %
    #             (timestamp, len(results_list)))

    # return results_list, 200
    count_item = 1
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Inventory Item at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get('type') == 'item':
                logger.info(msg)
                if count_item == index:
                    print(msg)
                    return msg["payload"], 200
                else:
                    count_item+= 1
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find Inventory Item at index %d" % index)
    return { "message": "Not Found"}, 404


def get_standard_order(index):
    # """ Gets new heart rate readings after the timestamp """

    # session = DB_SESSION()

    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    # readings = session.query(StandardOrder).filter(StandardOrder.date_created >=
    #                                                timestamp_datetime)

    # results_list = []

    # for reading in readings:
    #     results_list.append(reading.to_dict())

    # session.close()

    # logger.info("Query for Heart Rate readings after %s returns %d results" %
    #             (timestamp, len(results_list)))

    # return results_list, 200
    count_order = 1
    """ Get BP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving Inventory Item at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg.get('type') == 'order':
                logger.info(msg)
                if count_order == index:
                    print(msg)
                    return msg["payload"], 200
                else:
                    count_order+= 1
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find Inventory Item at index %d" % index)
    return { "message": "Not Found"}, 404



def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "item":  # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            report_inventory_item(payload)
        elif msg["type"] == "order":  # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            report_standard_order(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8110)
