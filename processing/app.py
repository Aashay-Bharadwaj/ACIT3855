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
    
    obj = {"num_reports": stats['num_reports'], "num_infrared_reports": stats["num_infrared_reports"],
           "num_patrol_reports": stats["num_patrol_reports"], "num_positive_status": stats["num_positive_status"], "timestamp": stats['timestamp']}
    
    logger.debug(f'{obj}')

    logger.info("Request has completed.")

    return Response(json.dumps(obj), 200)
    


def populate_stats():
    logger.info("Start Periodic Processing")

    with open(app_config['datastore']['filename'], 'r') as file:
        stats = json.load(file)
    
    time = stats['timestamp']
    print(time)
    next_time = datetime.datetime.now()
    patrols = requests.get(f'{app_config["eventstore"]["url"]}/reports/patrols', params = {"timestamp": time})
    infrared = requests.get(f'{app_config["eventstore"]["url"]}/reports/infrared', params = {"timestamp": time})
    results = []
    infra = 0
    pat = 0
    try:
        for i in patrols.json():
            results.append(i)
            infra += 1
        for i in infrared.json():
            results.append(i)
            pat += 1
    except:
        logger.info('Json decode error. Results list is empty.')
        return
    if patrols.status_code != 200:
        logger.error("Status Code not 200")
    print(results)
    logger.info(f'{len(results)} results were received.')

    json_obj = {'num_reports': stats['num_reports'] + len(results), 'num_infrared_reports': stats['num_infrared_reports'] + infra,
                'num_patrol_reports': stats['num_patrol_reports'] + pat, 'num_positive_status': stats['num_positive_status'] + 0, 'timestamp':next_time
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
