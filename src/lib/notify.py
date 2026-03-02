import boto3


class Notify:
    def __init__(self, topic_arn: str, phone: str):
        # The `topic_arn` defines a subscription group emails may subscribe to.
        self.topic_arn = topic_arn
        self.phone = phone
        self.sns = boto3.client("sns")

    def text(self, message: str):
        """
        Send an SMS to the phone number for "cases gone wrong."
        """
        self.sns.publish(PhoneNumber=self.phone, Message=message)

    def email(self, subject: str, message: str):
        """
        Send an email to those listening to this topic.
        """
        self.sns.publish(TopicArn=self.topic_arn, Subject=subject, Message=message)
