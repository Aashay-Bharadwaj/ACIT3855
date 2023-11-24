import connexion
import datetime
import requests
import json
import yaml
import logging, logging.config
from apscheduler.schedulers.background import BackgroundScheduler




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
    except:
        return Response("Status records do not exist", 404)
    
    obj = {"receiver": status['receiver'], "storage": status["storage"],
           "audit": status["audit"], "processing": status["processing"], "last_updated": status['last_updated']}
    
    logger.debug(f'{obj}')

    logger.info("Request has completed.")

    return Response(json.dumps(obj), 200)
    


def populate_status():
    logger.info("Starting service check process")

    with open(app_config['datastore']['filename'], 'r') as file:
        stats = json.load(file)
    
    time = stats['last_updated']
    print(time)
    next_time = datetime.datetime.now()
    start_time = time.time()
    audit = requests.get(app_config["eventstore"]["url"] + "/health")
    end_time = time.time()

    elapsed_time = end_time - start_time
    if elapsed_time > 5:
        stats['audit'] = "down"
        print(f"Request took {elapsed_time} seconds, which is more than 5 seconds.")
    else:
        stats['audit'] = "running"
        print(f"Request took {elapsed_time} seconds.")
     
    # order = requests.get(app_config["eventstore"]["url"] + "/standard-order?timestamp=" + '2013-11-23T08:30:00Z')
    print(stats)
def get_health():
    return 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_status,
                'interval',
                seconds=app_config['scheduler']['period_sec'])
    sched.start()
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port='8120')
