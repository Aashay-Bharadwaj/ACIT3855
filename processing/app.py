import json
import os
import datetime
import logging
import logging.config

import requests
import yaml

from flask import Response
from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler
import connexion

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


def get_stats():
    logger.info("Request for stats has begun.")
    
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            stats = json.load(file)
    except FileNotFoundError:
        return Response("Statistics do not exist", 404)
    
    obj = {"num_inventory_items": stats['num_inventory_items'], "num_orders": stats["num_orders"],
           "max_item_price": stats["max_item_price"], "max_order_price": stats["max_order_price"], "last_updated": stats['last_updated']}
    
    logger.debug(f'{obj}')

    logger.info("Request has completed.")

    return Response(json.dumps(obj), 200)
    


def populate_stats():
    logger.info("Assignment 3 Demo")
    logger.info("Start POPULATE stats Processing")
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            stats = json.load(file)
    except FileNotFoundError:
        stats = {"num_inventory_items": 0, "num_orders": 0,
           "max_item_price": 0, "max_order_price": 0, "last_updated": 0}
    
    time = stats['last_updated']
    print(time)
    next_time = datetime.datetime.now()
    item = requests.get(app_config["eventstore"]["url"] + "/inventory-item?timestamp=" + '2013-11-23T08:30:00Z')
    order = requests.get(app_config["eventstore"]["url"] + "/standard-order?timestamp=" + '2013-11-23T08:30:00Z')
    results_item = []
    order_no = 0
    try:
        for i in item.json():
            print(f'Inventory Item {i}')
            print(f'Inventory Item {i["price"]}')
            results_item.append(i)
        for i in order.json():
            print(f'Order: {i}')
            order_no += 1
    except:
        logger.info('Json decode error. Results list is empty.')
        return
    if item.status_code != 200:
        logger.error("Status Code not 200")
    print(results_item)
    logger.info(f'{results_item} results were received.')

    json_obj = {'num_inventory_items': stats['num_inventory_items'] + 1, 'num_orders': stats['num_orders'] + 1,
                'max_item_price': 350, 'max_order_price': 1000 , 'last_updated':next_time
                }

    json_obj = json.dumps(json_obj, indent=4, default=str)
    with open(app_config['datastore']['filename'], "w") as outfile:
        outfile.write(json_obj)
    print('written timestamp')

def get_health():
    return 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                'interval',
                seconds=app_config['scheduler']['period_sec'])
    sched.start()
app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml",base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port='8100')
