import os
import random
import string

SOURCE_PROJECT = os.getenv("SOURCE_PROJECT")
SOURCE_INSTANCE = os.getenv("SOURCE_INSTANCE")
SOURCE_INSTANCE_REGION = os.getenv("SOURCE_INSTANCE_REGION")
DEST_PROJECT = os.getenv("DEST_PROJECT")
DEST_INSTANCE = os.getenv("DEST_INSTANCE")
DEST_INSTANCE_REGION = os.getenv("DEST_INSTANCE_REGION")
DEST_INSTANCE_IP_ADDRESS_TYPE = os.getenv("DEST_INSTANCE_IP_ADDRESS_TYPE", "PRIVATE").upper()
DEST_DATABASE_HOST = os.getenv("DEST_DATABASE_HOST")

SOURCE_USER = os.getenv("SOURCE_USER")
SOURCE_USER_TEMP_PASSWORD = os.getenv("SOURCE_USER_TEMP_PASSWORD",
                                   ''.join(random.choice(string.ascii_letters + string.digits) for i in range(13)))
SOURCE_DATABASE_NAME = os.getenv("SOURCE_DATABASE_NAME", SOURCE_USER)

DEST_NEW_USER = os.getenv("DEST_NEW_USER")
DEST_NEW_USER_PASSWORD = os.getenv("DEST_NEW_USER_PASSWORD")
DEST_DATABASE_NAME = os.getenv("DEST_DATABASE_NAME", DEST_NEW_USER)

DEST_DATABASE_PORT = os.getenv("DEST_DATABASE_PORT", 5432)

ANONYMIZE_SQL_SCRIPT_PATH = os.getenv("ANONYMIZE_SQL_SCRIPT_PATH")
PCAPI_ROOT_PATH = os.getenv("PCAPI_ROOT_PATH")
IMPORT_USERS_SCRIPT_PATH = os.getenv("IMPORT_USERS_SCRIPT_PATH")
USERS_CSV_PATH = os.getenv("USERS_CSV_PATH")

POST_PROCESS = os.getenv("POST_PROCESS") == "TRUE"
TABLES_TO_EMPTY = os.getenv("TABLES_TO_EMPTY", "").split(" ") if os.getenv("TABLES_TO_EMPTY") != "" else []

DEST_DATABASE_HOST = os.getenv("DEST_DATABASE_HOST")
DEST_DATABASE_PORT = os.getenv("DEST_DATABASE_PORT", 5432)
SOURCE_DATABASES_TO_EXPORT = os.getenv("SOURCE_DATABASES_TO_EXPORT")
DUMP_BUCKET = os.getenv("DUMP_BUCKET")
