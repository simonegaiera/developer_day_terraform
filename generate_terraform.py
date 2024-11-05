import csv
from jinja2 import Template
from dotenv import load_dotenv
import os
import sys


# Load environment variables from .env file
def load_env_variables():
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

def csv_to_dict_array(csv_file_path, filter_func=None):
    dict_array = []
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if filter_func is None or filter_func(row):
                dict_array.append(row)
    return dict_array

def generate_configs(users, template_string, common_database=None):
    template = Template(template_string)
    configs = []
    for user in users:
        user['username'] = f"{user['name']}_{user['surname']}"
        user['password'] = os.getenv('USERS_PASSWORD')
        config = template.render(user=user, common_database=common_database)
        configs.append(config)
    return configs

def write_configs_to_file(configs, file_path):
    with open(file_path, 'w') as file:
        for config in configs:
            file.write(config)
            file.write("\n")

def main():
    load_env_variables()

    # Get users
    users = csv_to_dict_array('./user_list.csv', lambda row: not row['email'].endswith('@mongodb.com'))
    mongo_users = csv_to_dict_array('./user_list.csv', lambda row: row['email'].endswith('@mongodb.com'))

    # Create Database User terraform file
    with open('./terraform-template/terraform_database_user.tmpl', 'r') as file:
        template_db_user = file.read()
    database_users_tf = generate_configs(users, template_db_user, os.getenv('MONGO_DATABASE_NAME'))
    write_configs_to_file(database_users_tf, './terraform/database_users.tf')

    # Create customer invitations
    with open('./terraform-template/terraform_invitation_mongodb.tmpl', 'r') as file:
        template_mongo_invitation = file.read()
    database_mongo_tf = generate_configs(mongo_users, template_mongo_invitation)
    
    with open('./terraform-template/terraform_invitation.tmpl', 'r') as file:
        template_team_invitation = file.read()
    database_teams_tf = generate_configs(users, template_team_invitation)

    write_configs_to_file(database_mongo_tf + database_teams_tf, './terraform/project_invitation.tf')

if __name__ == "__main__":
    main()
