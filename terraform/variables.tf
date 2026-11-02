variable "kubeconfig_path" {
  description = "Path to kubeconfig for the target cluster"
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "kubectl context to use (e.g. docker-desktop, minikube, kind-kind)"
  type        = string
  default     = "docker-desktop"
}

variable "app_namespace" {
  type    = string
  default = "car-price"
}

variable "monitoring_namespace" {
  type    = string
  default = "monitoring"
}

variable "prometheus_stack_version" {
  type    = string
  default = "61.3.2"
}

variable "grafana_admin_password" {
  type      = string
  sensitive = true
  default   = "admin"
}
