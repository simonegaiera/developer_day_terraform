
#
# Configure the MongoDB Atlas Provider
#
terraform {
  required_providers {
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
      version = "1.21.4"
    }
  }
}
provider "mongodbatlas" {
  public_key  = var.public_key
  private_key = var.private_key
}

# data "mongodbatlas_roles_org_id" "org" {}

# resource "mongodbatlas_project" "project" {
#   name   = var.project_name
#   org_id = data.mongodbatlas_roles_org_id.org.org_id

#   limits {
#     name = "atlas.project.security.databaseAccess.users"
#     value = 250
#   }
# }

#
# Create a Shared Tier Cluster
#
resource "mongodbatlas_cluster" "create-cluster" {
  project_id   = var.project_id
  name         = var.cluster_name
  cluster_type = var.cluster_type

  replication_specs {
    num_shards = 1
    regions_config {
      region_name     = var.cluster_region
      electable_nodes = 3
      priority        = 7
      read_only_nodes = 0
    }
  }
  cloud_backup = true
  pit_enabled = true
  auto_scaling_disk_gb_enabled = var.auto_scaling_disk_gb_enabled
  mongo_db_major_version       = var.mongo_db_major_version
  provider_name               = var.atlas_provider_name
  provider_instance_size_name = var.atlas_provider_instance_size_name
}

output "connection_strings" {
  value = ["${mongodbatlas_cluster.create-cluster.connection_strings}"]
}

# resource "mongodbatlas_project_ip_access_list" "all" {
#   project_id = var.project_id
#   cidr_block = "0.0.0.0/0"
#   comment    = "accept all"
# }

resource "mongodbatlas_database_user" "user-main" {
  username           = var.mongodb_atlas_database_username
  password           = var.mongodb_atlas_database_user_password
  project_id         = var.project_id
  auth_database_name = "admin"

  roles {
    role_name     = "atlasAdmin"
    database_name = "admin"
  }
}
