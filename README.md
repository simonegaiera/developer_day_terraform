
## Create Enviroment

### Create Terraform Files
1. Create a "terraform" folder if doesn't exists
2. Copy the files into the "terraform" folder and change accordingly:
    - main.tf
    - terraform.tfvars
    - variables.tf
3. Modify accordingly if the project already exist
4. Create the user_list.csv to include all your user, from the template
5. Create the ".env" file from the template
6. Run "python create_env.py" to generate the Terraform file for Database Users and Project Invitation


### Run Terraform
1. Modify the variables.tfvars file accordingly (change API keys with Organization Project Creator, Organization Member and Project name)
2. Run Terraform (terraform init, terraform plan, terraform apply)


### Populate Database
1. Verify the ".env" file
2. Run the file "populate_collection.py" to create all the collection for the user
