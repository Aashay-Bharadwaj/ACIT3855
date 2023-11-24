import connexion
import datetime
import requests
import json
import yaml
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Response

# Load configurations
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_status():
    logger.info("Request for Status check has begun.")
    
    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            status = json.load(file)
    except FileNotFoundError:
        return Response("Status records do not exist", 404)
    
    obj = {
        "receiver": status.get('receiver', 'unknown'),
        "storage": status.get("storage", 'unknown'),
        "audit": status.get("audit", 'unknown'),
        "processing": status.get("processing", 'unknown'),
        "last_updated": status.get('last_updated', 'unknown')
    }
    
    logger.debug(f'{obj}')

    logger.info("Request has completed.")

    return Response(json.dumps(obj), status=200, mimetype='application/json')

def populate_status():
    logger.info("Starting service check process")

    try:
        with open(app_config['datastore']['filename'], 'r') as file:
            stats = json.load(file)
    except FileNotFoundError:
        logger.error("Datastore file not found.")
        return

    time = stats.get('last_updated', datetime.datetime.now())
    print(time)

    start_time = time.time()
    audit = requests.get(app_config["eventstore"]["url"] + "/health")
    end_time = time.time()

    elapsed_time = end_time - start_time

    if elapsed_time > 5:
        stats['audit'] = "down"
        logger.warning(f"Request took {elapsed_time} seconds, which is more than 5 seconds.")
    else:
        stats['audit'] = "running"
        logger.info(f"Request took {elapsed_time} seconds.")

    print(stats)

def get_health():
    return "OK", 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_status, 'interval', seconds=20)
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8120)
