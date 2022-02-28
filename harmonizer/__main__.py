import logging
import time

import pandas as pd
import settings
from utils.kafka import read_from_kafka
from utils.utils import read_config, log_string, load_plugins
from utils.mongo import mongo_logger


if __name__ == '__main__':
    config = read_config(settings.conf_file)
    sources_available = load_plugins(settings)
    consumer = read_from_kafka(config['kafka']['topic'], config["kafka"]['group_harmonize'],
                               config['kafka']['connection'])
    # while True:
    #     consumer.resume()
    #     x = consumer.next_v2()
    #     consumer.commit()
    #     consumer.pause()
    try:
        for x in consumer:
            start = time.time()
            message = x.value
            df = pd.DataFrame.from_records(message['data'])
            mapper = None
            kwargs_function = {}
            if 'logger' in message:
                mongo_logger.import_log(message['logger'], "harmonize")
            message_part = ""
            if 'message_part' in message:
                message_part = message['message_part']
            # log_string(f"received part {message_part} from {message['source']} to harmonize")
            for k, v in sources_available.items():
                if message['source'] == k:
                    # log_string(f"{k}, {v}, {message['source']}")
                    mapper = v.get_mapper(message)
                    kwargs_function = v.get_kwargs(message)
                    df = v.transform_df(df)
                    break
            if mapper:
                # log_string("mapping data")
                try:
                    mapper(df.to_dict(orient="records"), **kwargs_function)
                    # log_string(f"part {message_part} from {message['source']} harmonized successfully")
                except Exception as e:
                    log_string(f"part {message_part} from {message['source']} harmonized error: {e}")
            duration = time.time() - start
            print(duration)
    except Exception as e:
        time.sleep(10)
        print(e)
