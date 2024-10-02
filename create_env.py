import csv
from jinja2 import Template
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
    'MONGO_DATABASE_NAME',
    'USERS_PASSWORD'
]

missing_variables = [var for var in required_variables if os.getenv(var) is None]
if missing_variables:
    print(f"Error: Missing required environment variables: {', '.join(missing_variables)}", file=sys.stderr)
    sys.exit(1)

# This creates one Project for all the users and one database for each user

common_database = os.getenv('MONGO_DATABASE_NAME')
users_password = os.getenv('USERS_PASSWORD')

def csv_to_dict_array(csv_file_path):
    dict_array = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if not row['email'].endswith('@mongodb.com'):
                dict_array.append(row)
    return dict_array

def csv_to_dict_array_mongo(csv_file_path):
    dict_array = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['email'].endswith('@mongodb.com'):
                dict_array.append(row)
    return dict_array


def generate_user_configs(users, common_database, template_string):
    template = Template(template_string)
    configs = []
    for user in users:
        user['username'] = user['name'] + '_' + user['surname']
        user['password'] = users_password
        config = template.render(user=user, common_database=common_database)
        configs.append(config)
    return configs

def generate_invitation_configs(users, template_string):
    template = Template(template_string)
    configs = []
    for user in users:
        user['username'] = user['name'] + '_' + user['surname']
        user['email'] = user['email']
        config = template.render(user=user)
        configs.append(config)
    return configs

# Get users
users = csv_to_dict_array('./user_list.csv')
mongo_users = csv_to_dict_array_mongo('./user_list.csv')

# Create Database User terraform file
with open('./terraform-template/terraform_database_user.tmpl', 'r') as file:
    template_db_user = file.read()
database_users_tf = generate_user_configs(users, common_database, template_db_user)

with open('./terraform/database_users.tf', 'w') as file:
    for config in database_users_tf:
        file.write(config)
        file.write("\n")

# Create customer invitations
with open('./terraform-template/terraform_invitation_mongodb.tmpl', 'r') as file:
    template_team = file.read()

database_mongo_tf = generate_invitation_configs(mongo_users, template_team)

with open('./terraform-template/terraform_invitation.tmpl', 'r') as file:
    template_team = file.read()

database_teams_tf = generate_invitation_configs(users, template_team)

with open('./terraform/project_invitation.tf', 'w') as file:
    for config in database_mongo_tf:
        file.write(config)
        file.write("\n")
    
    for config in database_teams_tf:
        file.write(config)
        file.write("\n")
