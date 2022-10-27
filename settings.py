import os

from dotenv import load_dotenv

load_dotenv()
conf_file = os.getenv("CONFIG_FILE")
kafka_message_size = 10
secret_password = os.getenv("SECRET_PASSWORD")
namespace_mappings = {"bigg": "bigg", "wgs": "wgs"}
ts_buckets = 10000000
buckets = 20
sources_priorities = ["Greece", "Czech"]
countries = ["ES", "BG", "GR", 'CZ']
