from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import csv
from dotenv import load_dotenv
import os
import sys
import requests
import json
from requests.auth import HTTPDigestAuth

def load_env_variables():
    # Load environment variables from .env file
    dotenv_path = '.env'
    if not os.path.exists(dotenv_path):
        print(f"Error: .env file not found at path {dotenv_path}", file=sys.stderr)
        sys.exit(1)

    load_dotenv(dotenv_path)

    required_variables = [
        'MONGO_CONNECTION_STRING',
        'MONGO_DATABASE_NAME',
        'TERRAFORM_VARIABLE_FILE_NAME'
    ]

    missing_variables = [var for var in required_variables if os.getenv(var) is None]
    if missing_variables:
        print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
        sys.exit(1)

def load_terraform_variables():
    # Load environment variables from terraform file
    dotenv_path = './terraform/' + os.getenv('TERRAFORM_VARIABLE_FILE_NAME')
    if not os.path.exists(dotenv_path):
        print(f"Error: .env file not found at path {dotenv_path}", file=sys.stderr)
        sys.exit(1)

    load_dotenv(dotenv_path, override=False)

    # Get variables from environment
    terraform_required_variables = [
        'public_key',
        'private_key',
        'project_id'
    ]

    missing_variables = [var for var in terraform_required_variables if os.getenv(var) is None]
    if missing_variables:
        print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
        sys.exit(1)


def csv_to_dict_array(csv_file_path):
    databases = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if not row['email'].endswith('@mongodb.com'):
                databases.append(row['name'] + '_' + row['surname'])
    return databases

def get_client():
    client = MongoClient(os.getenv('MONGO_CONNECTION_STRING'), server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)

def load_sample_dataset():
    atlas_auth = HTTPDigestAuth(os.getenv('public_key'), os.getenv('private_key'))
    atlas_v2_headers = {"Accept": "application/vnd.atlas.2023-02-01+json", "Content-Type": "application/json"}

    load_dataset = requests.post('https://cloud.mongodb.com/api/atlas/v2/groups/{}/sampleDatasetLoad/{}'
                                 .format(os.getenv('project_id'), os.getenv('MONGO_DATABASE_NAME')),
                                 headers=atlas_v2_headers, auth=atlas_auth)

    if load_dataset.status_code == 201:
        print('Sample data loaded')
    else:
        print('ERROR {}! {}'.format(load_dataset.status_code, load_dataset.json()))
        sys.exit(1)

def create_user_collection(db_name, client, collections_list):
    for collection in collections_list:
        client[common_database][collection].aggregate([{'$out': {'db': db_name, 'coll': collection}}])


load_env_variables()
common_database = os.getenv('MONGO_DATABASE_NAME')

client = get_client()
databases = client.list_database_names()

if common_database in databases:
    print(f"Database '{common_database}' exists.")
else:
    print(f"Database '{common_database}' does not exist. Creating.")
    load_sample_dataset()

users = csv_to_dict_array('./user_list.csv')
users.append(common_database)

collections_list = client[common_database].list_collection_names()

for database in users:
    if database in databases:
        print(f"Database '{database}' exists.")
    else:
        print(f"Database '{database}' does not exist. Creating.")
        create_user_collection(database, client, collections_list)
