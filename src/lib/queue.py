import boto3
import json


class Queue:
    def __init__(self, queue_url: str):
        self.sqs = boto3.client("sqs")
        self.queue_url = queue_url

    def send(self, message: dict):
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
        )