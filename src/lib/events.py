import boto3

class Events:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.cloudwatch = boto3.client("cloudwatch")

    """
    Logs a successful transaction with inflow and outflow, to call once
    the order is fully shipped.
    """
    def transaction(self, inflow: float, outflow: float):
        self._metric("Inflow", inflow)
        self._metric("Outflow", outflow)

    def _metric(self, name: str, value: float, unit: str = "None"):
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[{"MetricName": name, "Value": value, "Unit": unit}],
        )
