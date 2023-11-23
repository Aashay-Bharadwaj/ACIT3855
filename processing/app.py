import connexion
import datetime
import requests
import json
from flask import Response
from flask_cors import CORS, cross_origin
import yaml
import logging, logging.config
import uuid
from apscheduler.schedulers.background import BackgroundScheduler

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_stats():
    logger.info("Request for stats has begun.")
    
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            stats = json.load(file)
    except:
        return Response("Statistics do not exist", 404)
    
    obj = {"num_inventory_items": stats['num_inventory_items'], "num_orders": stats["num_orders"],
           "max_item_price": stats["max_item_price"], "max_order_price": stats["max_order_price"], "last_updated": stats['last_updated']}
    
    logger.debug(f'{obj}')

    logger.info("Request has completed.")

    return Response(json.dumps(obj), 200)
    


def populate_stats():
    logger.info("Start POPULATE stats Processing")

    with open(app_config['datastore']['filename'], 'r') as file:
        stats = json.load(file)
    
    time = stats['last_updated']
    print(time)
    next_time = datetime.datetime.now()
    item = requests.get(app_config["eventstore"]["url"] + "/inventory-item?timestamp=" + '2013-11-23T08:30:00Z')
    order = requests.get(app_config["eventstore"]["url"] + "/standard-order?timestamp=" + '2013-11-23T08:30:00Z')
    results_item = []
    results_order = []
    item_no = 0
    order_no = 0
    try:
        for i in item.json():
            print(f'Inventory Item {i}')
            results_item.append(i)
            item_no += 1
        for i in order.json():
            results_order.append(i)
            order_no += 1
    except:
        logger.info('Json decode error. Results list is empty.')
        return
    if item.status_code != 200:
        logger.error("Status Code not 200")
    print(results_item)
    logger.info(f'{results_item} results were received.')

    json_obj = {'num_inventory_items': stats['num_inventory_items'] + len(results_item), 'num_orders': stats['num_orders'] + len(results_order),
                'max_item_price': stats['max_item_price'], 'max_order_price': stats['max_order_price'] , 'last_updated':next_time
                }

    json_obj = json.dumps(json_obj, indent=4, default=str)
    with open(app_config['datastore']['filename'], "w") as outfile:
        outfile.write(json_obj)
    print('written timestamp')

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                'interval',
                seconds=app_config['scheduler']['period_sec'])
    sched.start()

app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port='8100')
