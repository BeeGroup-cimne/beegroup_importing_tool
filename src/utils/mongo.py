from datetime import datetime
from pymongo import MongoClient


class mongo_connection(object):
    @classmethod
    def __connection_mongo__(cls, config):
        cli = MongoClient("mongodb://{user}:{pwd}@{host}:{port}/{db}".format(**config))
        db = cli[config['db']]
        return db

    def __new__(cls, mongo_conf):
        return cls.__connection_mongo__(mongo_conf)


class mongo_logger(object):
    mongo_conf = None
    collection = None
    mongo_connection = None
    log_id = None
    db = None
    log_type = None

    @staticmethod
    def get_connection():
        return mongo_logger.mongo_connection

    @staticmethod
    def __connect__(mongo_conf, collection):
        mongo_logger.mongo_conf = mongo_conf
        mongo_logger.collection = collection
        mongo_logger.mongo_connection = mongo_connection(mongo_logger.mongo_conf)
        mongo_logger.db = mongo_logger.mongo_connection[mongo_logger.collection]

    @staticmethod
    def create(mongo_conf, collection, log_type,  **kwargs):
        mongo_logger.__connect__(mongo_conf, collection)
        mongo_logger.log_type = log_type
        log_document = {
            "logs": {
                "gather": [],
                "store": [],
                "harmonize": []
            }
        }
        log_document.update(kwargs)
        mongo_logger.log_id = mongo_logger.db.insert_one(log_document).inserted_id

    @staticmethod
    def export_log():
        return {
            "mongo_conf": mongo_logger.mongo_conf,
            "collection": mongo_logger.collection,
            "log_id": mongo_logger.log_id
        }

    @staticmethod
    def import_log(exported_info, log_type):
        mongo_logger.__connect__(exported_info['mongo_conf'], exported_info['collection'])
        mongo_logger.log_id = exported_info['log_id']
        mongo_logger.log_type = log_type

    @staticmethod
    def log(message):
        if any([mongo_logger.db is None, mongo_logger.db is None, mongo_logger.log_type is None]):
            return
        mongo_logger.db.update_one({"_id": mongo_logger.log_id},
                                   {"$push": {
                                       f"logs.{mongo_logger.log_type}": f"{datetime.utcnow()}: \
                                       {message}"}})


def save_to_mongo(mongo, documents, index_field=None):
    documents_ = documents.copy()
    if index_field:
        for d in documents_:
            d['_id'] = d.pop(index_field)
    if documents:
        mongo.remove()
        mongo.insert_many(documents_)
