{{- define "helm-chart-label" -}}
  {{- if .Values.renderHelmLabels -}}
"helm.sh/chart": "{{ .Chart.Name }}-{{ .Chart.Version }}"
  {{- end -}}
{{- end -}}