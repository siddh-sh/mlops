output "app_namespace" {
  value = kubernetes_namespace.app.metadata[0].name
}

output "grafana_port_forward" {
  value = "kubectl -n ${var.monitoring_namespace} port-forward svc/kube-prometheus-stack-grafana 3000:80"
}
