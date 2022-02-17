import os
from dotenv import load_dotenv
load_dotenv()
conf_file = os.getenv("CONFIG_FILE")
kafka_message_size = os.getenv("KAFKA_MESSAGE_SIZE")
secret_password = os.getenv("SECRET_PASSWORD")
