import argparse
from datetime import datetime
import utils
from .read_xml_file import read_xml_certificate


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--building", "-b", help="The building importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    args = ap.parse_args(arguments)
    mongo_logger = utils.mongo.mongo_logger
    mongo_logger.create(config['mongo_db'], config['data_sources'][config['source']]['log'], 'gather', user=args.user,
                        log_exec=datetime.utcnow())
    try:
        cert = read_xml_certificate(args.file)
    except Exception as e:
        cert = {}
        utils.utils.log_string(f"could not parse file: {e}")
        exit(1)

    try:
        cert.pop("@version")
    except:
        pass

    for k, v in cert.items():
        v['building_organization_code'] = args.building

        if args.store == "kafka":
            utils.utils.log_string(f"saving to kafka", mongo=False)
            try:
                kafka_message = {
                    "namespace": args.namespace,
                    "user": args.user,
                    "collection_type": k,
                    "source": config['source'],
                    "row_keys": ["building_organization_code"],
                    "logger": mongo_logger.export_log(),
                    "data": [v]
                }
                k_harmonize_topic = config["kafka"]["topic"]
                utils.kafka.save_to_kafka(topic=k_harmonize_topic, info_document=kafka_message,
                                          config=config['kafka']['connection'], batch=settings.kafka_message_size)
            except Exception as e:
                utils.utils.log_string(f"error when sending message: {e}")
        elif args.store == "hbase":
            utils.utils.log_string(f"saving to hbase", mongo=False)
            try:
                h_table_name = f"raw_ceec3x_static_{k}__{args.user}"
                utils.hbase.save_to_hbase([v], h_table_name, config['hbase_store_raw_data'], [("info", "all")],
                                          row_fields=["building_organization_code"])
            except Exception as e:
                utils.utils.log_string(f"error saving to hbase: {e}")
        else:
            utils.utils.log_string(f"store {args.store} is not supported")
