import connexion
from connexion import NoContent

import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests

import logging.config
import yaml

# External Application Configuration
with open('SampleProcessor/app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open('SampleProcessor/log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_stats():
    """ Gets processing stats """

    if os.path.isfile(app_config["datastore"]["filename"]):
        fh = open(app_config["datastore"]["filename"])
        full_stats = json.load(fh)
        fh.close()

        stats = {}
        if "num_inventory_items" in full_stats:
            stats["num_inventory_items"] = full_stats["num_inventory_items"]
        if "max_item_price" in full_stats:
            stats["max_item_price"] = full_stats["max_item_price"]
        if "num_orders" in full_stats:
            stats["num_orders"] = full_stats["num_orders"]
        if "max_order_price" in full_stats:
            stats["max_order_price"] = full_stats["max_order_price"]

        logger.info("Found valid stats")
        logger.debug(stats)

        return stats, 200

    return NoContent, 404


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    stats = get_latest_processing_stats()

    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    if "last_updated" in stats:
        last_updated = stats["last_updated"]

    response = requests.get(app_config["eventstore"]["url"] + "/inventory-item?timestamp=" + last_updated)

    if response.status_code == 200:
        if "num_inventory_items" in stats.keys():
            stats["num_inventory_items"] += len(response.json())
        else:
            stats["num_inventory_items"] = len(response.json())

        for event in response.json():
            if "max_item_price" in stats.keys() and \
                event["price"] > stats["max_item_price"]:
                stats["max_item_price"] = event["price"]
            elif "max_item_price" not in stats.keys():
                stats["max_item_price"] = event["price"]

            logger.debug("Processed Inventory Item event with id of %s" % event["trace_id"])

        logger.info("Processed %d Inventory Item readings" % len(response.json()))

    response = requests.get(app_config["eventstore"]["url"] + "/standard-order?timestamp=" + last_updated)

    if response.status_code == 200:
        if "num_orders" in stats.keys():
            stats["num_orders"] += len(response.json())
        else:
            stats["num_orders"] = len(response.json())

        for event in response.json():
            if "max_order_price" in stats.keys() and \
                    event["total_amount"] > stats["max_order_price"]:
                stats["max_order_price"] = event["total_amount"]
            elif "max_order_price" not in stats.keys():
                stats["max_order_price"] = event["total_amount"]

            logger.debug("Processed Standard Order event with id of %s" % event["trace_id"])

        logger.info("Processed %d Standard Order readings" % len(response.json()))

    stats["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    write_processing_stats(stats)

    logger.info("Done Periodic Processing")


def get_latest_processing_stats():
    """ Gets the latest stats object, or None if there isn't one """
    if os.path.isfile(app_config["datastore"]["filename"]):
        fh = open(app_config["datastore"]["filename"])
        full_stats = json.load(fh)
        fh.close()
        return full_stats

    return {"num_inventory_items": 0,
            "num_orders": 0,
            "max_item_price": 0,
            "max_order_price": 0,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}


def write_processing_stats(stats):
    """ Writes a new stats object """
    fh = open(app_config["datastore"]["filename"], "w")
    fh.write(json.dumps(stats))
    fh.close()


def init_scheduler():
    """ Initializes the periodic background processing """
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
