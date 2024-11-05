import os
import sys
import csv
import time
import requests
from requests.auth import HTTPDigestAuth
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi


def load_env_variables():
    """Load environment variables from .env file."""
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
    """Load environment variables from the Terraform variable file."""
    terraform_file_path = os.path.join('terraform', os.getenv('TERRAFORM_VARIABLE_FILE_NAME'))
    if not os.path.exists(terraform_file_path):
        print(f"Error: Terraform variable file not found at path {terraform_file_path}", file=sys.stderr)
        sys.exit(1)

    load_dotenv(terraform_file_path, override=False)

    terraform_required_variables = [
        'public_key',
        'private_key',
        'project_id',
        'cluster_name'
    ]

    missing_variables = [var for var in terraform_required_variables if os.getenv(var) is None]
    if missing_variables:
        print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
        sys.exit(1)

def csv_to_dict_array(csv_file_path):
    """Convert CSV file to a list of user identifiers."""
    databases = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if not row['email'].endswith('@mongodb.com'):
                databases.append(f"{row['name']}_{row['surname']}")
    return databases

def get_client():
    """Create and return a MongoDB client."""
    client = MongoClient(os.getenv('MONGO_CONNECTION_STRING'), server_api=ServerApi('1'), tlsCAFile=certifi.where())
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

def load_sample_dataset():
    """Load a sample dataset into MongoDB Atlas."""
    atlas_auth = HTTPDigestAuth(os.getenv('public_key'), os.getenv('private_key'))
    atlas_v2_headers = {
        "Accept": "application/vnd.atlas.2023-02-01+json",
        "Content-Type": "application/json"
    }

    load_url = f'https://cloud.mongodb.com/api/atlas/v2/groups/{os.getenv("project_id")}/sampleDatasetLoad/{os.getenv("cluster_name")}'
    response = requests.post(load_url, headers=atlas_v2_headers, auth=atlas_auth)

    if response.status_code == 201:
        print('Sample data loading initiated...')
        dataset_id = response.json().get('_id')
        wait_for_loading(atlas_auth, atlas_v2_headers, dataset_id)
    else:
        handle_error(response)

def wait_for_loading(auth, headers, dataset_id):
    """Poll the loading status of the sample dataset."""
    loading = True
    while loading:
        status_url = f'https://cloud.mongodb.com/api/atlas/v2/groups/{os.getenv("project_id")}/sampleDatasetLoad/{dataset_id}'
        loaded_response = requests.get(status_url, headers=headers, auth=auth)

        if loaded_response.status_code != 200:
            handle_error(loaded_response)

        state = loaded_response.json().get('state')
        if state != 'WORKING':
            loading = False
            print('Sample data loaded successfully!')
        else:
            print("Loading dataset still running...")
            time.sleep(30)

def handle_error(response):
    """Handle errors from API responses."""
    print(f'ERROR {response.status_code}! {response.json()}', file=sys.stderr)
    sys.exit(1)

def create_user_collection(db_name, client, collections_list):
    """Create user collections in the specified database."""
    for collection in collections_list:
        client[db_name][collection].aggregate([{'$out': {'db': db_name, 'coll': collection}}])

def main():
    load_env_variables()
    common_database = os.getenv('MONGO_DATABASE_NAME')

    client = get_client()
    databases = client.list_database_names()

    if common_database in databases:
        print(f"Database '{common_database}' exists.")
    else:
        print(f"Database '{common_database}' does not exist. Creating.")
        load_terraform_variables()
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

if __name__ == "__main__":
    main()
