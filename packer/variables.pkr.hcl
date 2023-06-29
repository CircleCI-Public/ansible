variable "account_file" {
  type    = string
  default = ""
}

variable "image_name" {
  type    = string
  default = ""
}

variable "image_family" {
  type    = string
  default = ""
}

variable "project_id" {
  type    = string
  default = ""
}

variable "source_image" {
  type    = string
  default = ""
}

variable "source_image_family" {
  type    = string
  default = ""
}

variable "ssh_username" {
  type    = string
  default = ""
}

variable "zone" {
  type    = string
  default = ""
}

variable "skip_create_image" {
  type    = bool
  default = false
}

variable "playbook_file" {
  type    = string
  default = ""
}
