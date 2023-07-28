variable "image_tag" {
  type = string
  default = "latest"
}

variable "aws_region" {
  type = string
  description = "AWS Region to use for resources"
  default = "eu-north-1"
}

variable "subnet_a" {
  type = string
  description = "Availability zone of subnet A"
  default = "eu-north-1a"
}

variable "subnet_b" {
  type = string
  description = "Availability zone of subnet B"
  default = "eu-north-1b"
}

variable "task_definition_memory" {
  type = number
  description = "Task definition memory"
  default = 512
}

variable "task_definition_cpu" {
  type = number
  description = "Task definition cpu"
  default = 256
}
