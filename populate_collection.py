from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import subprocess
import csv
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
dotenv_path = '.env'
if not os.path.exists(dotenv_path):
    print(f"Error: .env file not found at path {dotenv_path}", file=sys.stderr)
    sys.exit(1)

load_dotenv(dotenv_path)

# Get variables from environment
required_variables = [
    'MONGO_CONNECTION_STRING',
    'MONGO_DATABASE_NAME',
    'MONGO_DUMP_FILE'
]

missing_variables = [var for var in required_variables if os.getenv(var) is None]
if missing_variables:
    print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
    sys.exit(1)

connection_string = os.getenv('MONGO_CONNECTION_STRING')
common_database = os.getenv('MONGO_DATABASE_NAME')
orig_database = common_database + "_orig"
dump_file = os.getenv('MONGO_DUMP_FILE')


def csv_to_dict_array(csv_file_path):
    databases = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if not row['email'].endswith('@mongodb.com'):
                databases.append(row['name'] + '_' + row['surname'])
    return databases

def get_client():
    client = MongoClient(connection_string, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)

def import_orig_dump():
    command = [
        "mongorestore",
        f'--uri="{connection_string}"',
        f'--nsFrom="{common_database}.*"',
        f'--nsTo="{orig_database}.*"',
        f"--archive={dump_file}",
        f"--gzip"
    ]
    subprocess.run(command, capture_output=True, text=True, check=True) 

def create_user_collection(db_name, client, collections_list):
    for collection in collections_list:
        client[orig_database][collection].aggregate([{'$out': {'db': db_name, 'coll': collection}}])


client = get_client()
databases = client.list_database_names()

if orig_database in databases:
    print(f"Database '{orig_database}' exists.")
else:
    print(f"Database '{orig_database}' does not exist. Creating.")
    import_orig_dump()

users = csv_to_dict_array('./user_list.csv')
users.append(common_database)

collections_list = client[orig_database].list_collection_names()

for database in users:
    if database in databases:
        print(f"Database '{database}' exists.")
    else:
        print(f"Database '{database}' does not exist. Creating.")
        create_user_collection(database, client, collections_list)
