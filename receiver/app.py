from connexion import NoContent
import yaml

import logging
import logging.config
import requests
import uuid
import random
import datetime

import json
from pykafka import KafkaClient
import connexion
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())

logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def report_inventory_item(body):
    """ Receives a heart rate event """

    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id

    logger.info("Received event Blood Pressure request with a unique id of %s and trace id of %s" %
                (body["SKU"], body["trace_id"]))
    # Deprecated
    # headers = {"Content-Type": "application/json"}
    # response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers)
    client = KafkaClient(hosts='%s:%d' % (app_config["events"]["hostname"], app_config["events"]["port"]))
    topic = client.topics[str.encode("events")]
    producer = topic.get_sync_producer()

    msg = {"type": "item",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event Blood Pressure response (Id: %s) with trace id of %s" %
                (body["SKU"], body["trace_id"]))

    return NoContent, 201 # NoContent means there is no response message


def report_standard_order(body):
    """ Receives a heart rate event """

    trace_id = str(uuid.uuid4())  # Can use uuid, random, datetime
    body["trace_id"] = trace_id

    logger.info("Received event Heart Rate request with a unique id of %s and trace id of %s" %
                (body["order_id"], body["trace_id"]))

    # Deprecated
    # headers = {"Content-Type": "application/json"}
    # response = requests.post(app_config["eventstore2"]["url"], json=body, headers=headers)
    client = KafkaClient(hosts='%s:%d' % (app_config["events"]["hostname"], app_config["events"]["port"]))
    topic = client.topics[str.encode("events")]
    producer = topic.get_sync_producer()

    msg = {"type": "order",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event Heart Rate response (Id: %s) with trace id of %s" %
                (body["order_id"], body["trace_id"]))

    return NoContent, 201 # NoContent means there is no response message

def get_health():
    return 200

# specification_dir is where to look for OpenAPI specifications. Empty string means
# look in the current directory.
app = connexion.FlaskApp(__name__, specification_dir='')
# openapi.yml - name of the OpenAPI Specification yaml file
# strict_validation - whether to valid requests parmameters or messages
# validate_responses - wheter to valid response codes or messages
app.add_api("openapi.yml",base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080) # Uses the built-in Flask server, port is explicit since
                       # we will be running multiple services in the future,
                       # each on a seporate port
