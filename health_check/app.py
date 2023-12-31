import connexion
import datetime
import requests
import json
import yaml
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Response
from flask_cors import CORS, cross_origin
CHECK_INTERVAL = 20
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
    
    # obj = {
    #     "receiver": 'down',
    #     "storage": 'down',
    #     "audit": 'down',
    #     "processing": 'down',
    #     "last_updated": "unknown"
    # }
    
    logger.debug(f'{status}')

    logger.info("Request has completed.")

    return Response(json.dumps(status), 200)

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

    try:    
        audit = requests.get(app_config["eventstore"]["url_audit"] + "/health", timeout=5)
        stats["audit"] = "Running"
    except requests.exceptions.RequestException:
        print("Timed out")
        stats["audit"] = "Down"
    try:    
        receiver = requests.get(app_config["eventstore"]["url_receiver"] + "/health", timeout=5)
        stats["receiver"] = "Running"
    except requests.exceptions.RequestException:
        print("Timed out")
        stats["receiver"] = "Down"
    try:    
        processing = requests.get(app_config["eventstore"]["url_processing"] + "/health", timeout=5)
        stats["processing"] = "Running"
    except requests.exceptions.RequestException:
        print("Timed out")
        stats["processing"] = "Down"
    try:    
        storage = requests.get(app_config["eventstore"]["url_storage"] + "/health", timeout=5)        
        stats["storage"] = "Running"
    except requests.exceptions.RequestException:
        print("Timed out")
        stats["storage"] = "Down"
        
        
        
    stats['last_update'] = datetime.datetime.now()
    stats = json.dumps(stats, indent=4, default=str)
    with open(app_config['datastore']['filename'], "w") as outfile:
        outfile.write(stats)
    print("Stats Written \n")
    print(stats)

def get_health():
    return "OK", 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_status, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()
app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml",base_path="/health-check", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port="8120")
