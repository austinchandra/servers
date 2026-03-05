import json
import os

from dotenv import load_dotenv

from lib.db import Database
from lib.errors import HttpError

load_dotenv()

db = Database(url=os.environ["DATABASE_URL"])


def handler(event, context):
    """
    Wrap a user order query with error-handling exception logic.
    """
    try:
        return _handle(event)
    except HttpError as e:
        return {"statusCode": e.status, "body": json.dumps({"error": e.message})}


def _handle(event):
    """
    Serve user order lookups given an order ID and email.
    """
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    order_id = path_params.get("id")
    email = query_params.get("email")

    if not order_id or not email:
        raise HttpError(400, "missing required parameters")

    try:
        order_id = int(order_id)
    except ValueError:
        raise HttpError(400, "invalid order id")

    order = db.get_order(order_id)

    if order is None or order.email != email:
        raise HttpError(404, "order not found or email is invalid")

    tracking_urls = [s.tracking_url for s in order.shipments if s.tracking_url]

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "receipt_url": order.receipt_url,
                "tracking_urls": tracking_urls,
            }
        ),
    }
