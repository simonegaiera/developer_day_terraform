# Developer Day Environment Preparation

## Create the cluster

### Step 1: Set Up Terraform Files

1. **Create the Terraform Directory**  
   - Check if a folder named "terraform" exists. If not, create it.

2. **Copy and Modify Terraform Files**  
   - Copy the following files into the "terraform" folder:
     - `main.tf`
     - `terraform.tfvars`
     - `variables.tf`
   - Adjust the contents of these files as necessary based on your project requirements.

3. **Update Existing Projects**  
   - If the project already exists, ensure to modify the files accordingly to reflect any changes.

4. **Create User List**  
   - Create a `user_list.csv` file using the provided template. This file should include all users relevant to your project.

5. **Set Up Environment Variables**  
   - Create a `.env` file based on the template provided. Ensure all necessary environment variables are included.

6. **Generate Terraform Configuration**  
   - Install the requirements
   - Execute the command:
     ```bash
     python generate_terraform.py
     ```  
   - This will generate the Terraform configuration files for Database Users and Project Invitations.

### Step 2: Run Terraform

1. **Modify Variables**  
   - Open the `terraform.tfvars` file and update the following:
     - API keys for Organization Project Creator
     - API keys for Organization Member
     - Project name

2. **Initialize and Apply Terraform**  
   - Run the following commands in sequence:
     ```bash
     terraform init
     terraform plan
     terraform apply
     ```

### Known Issues

- By default, projects are limited to **100 database users**. If you need to increase this limit, you can do so via the API using the `setProjectLimit` endpoint. The limit name is `atlas.project.security.databaseAccess.users`.

- For more details, refer to the [API documentation](https://www.mongodb.com/docs/atlas/reference/api-resources-spec/v2/#tag/Projects/operation/setProjectLimit).

- To increase the limit to **300 database users**, you can use the following `curl` command:

```bash
curl --user "PUBLIC_API_KEY:PRIVATE_API_KEY" \
  --digest \
  -H 'Content-Type: application/json' \
  -H "Accept: application/vnd.atlas.2023-01-01+json" \
  -X PATCH "https://cloud.mongodb.com/api/atlas/v2/groups/670423f2227e3573347794e6/limits/atlas.project.security.databaseAccess.users" \
  --data '{"value": 300, "name": "atlas.project.security.databaseAccess.users"}'
```

## Populate the Data

### AirBnB Workshop
1. **Verify Environment Variables**  
   - Double-check the contents of the `.env` file to ensure all variables are correctly set.

2. **Run Database Population Script**  
   - Execute the following command to create all necessary collections for the users:
     ```bash
     python populate_database_airbnb.py
     ```

### Library Dev Day
1. **Verify Environment Variables**  
   - Double-check the contents of the `.env` file to ensure all variables are correctly set.

2. **Run Database Population Script**  
   - Execute the following command to create all necessary collections for the users:
     ```bash
     python populate_database_library.py
     ```