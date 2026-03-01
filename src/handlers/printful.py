import json
from lib.db import Database
from lib.types import OrderStatus, Shipment
from lib.logs import Logs
import os
from dotenv import load_dotenv

load_dotenv()

db = Database(url=os.getenv("DATABASE_URL"))
log = Logs(log_group=os.environ["LOG_GROUP"])

"""
Capture the states of an order from Printful, and for some of these, such as "onhold,"
we prefer to deal with them in the application-level, rather than persist such states
to the database.
"""
PRINTFUL_STATUS_MAP = {
    "pending":   OrderStatus.pending,
    "inprocess": OrderStatus.pending,
    "onhold":    OrderStatus.pending,
    "inreview":  OrderStatus.pending,
    "fulfilled": OrderStatus.fulfilled,
    "failed":    OrderStatus.failed,
}

def handler(event, context):
    body = json.loads(event["body"])
    event_type = body.get("type")

    handlers = {
        "package_shipped":    handle_package_shipped,
        "order_fulfilled":    handle_order_fulfilled,
        "order_failed":       handle_order_failed,
        "order_put_hold":     handle_order_put_hold,
        "order_remove_hold":  handle_order_remove_hold,
    }

    fn = handlers.get(event_type)
    if fn:
        fn(body["data"])

    # Ignore any webhooks not listed, because we are not interested.
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"})
    }


def handle_package_shipped(data: dict):
    order_data = data["order"]
    shipment_data = data["shipment"]
    order_id = int(order_data["external_id"])

    order = db.get_order(order_id)
    if order is None:
        log.error("Order not found for package_shipped webhook", order_id=order_id)
        return

    # Add the new shipment
    db.upsert_shipment(Shipment(
        order_id=order_id,
        shipment_id=shipment_data["id"],
        tracking_url=shipment_data.get("tracking_url"),
    ))

    # Mark as partial unless the order is fulfilled—and ignore states "onhold", etc
    printful_status = order_data.get("status")
    new_status = OrderStatus.fulfilled if printful_status == "fulfilled" else OrderStatus.partial
    db.update_order(order_id, status=new_status)


def handle_order_fulfilled(data: dict):
    order_id = int(data["order"]["external_id"])
    db.update_order(order_id, status=OrderStatus.fulfilled)


def handle_order_failed(data: dict):
    order_id = int(data["order"]["external_id"])
    db.update_order(order_id, status=OrderStatus.failed)

def handle_order_put_hold(data: dict):
    # Order is on hold but still pending from our perspective
    order_id = int(data["order"]["external_id"])
    log.info("Order put on hold", order_id=order_id)


def handle_order_remove_hold(data: dict):
    # Order is back in processing
    order_id = int(data["order"]["external_id"])
    log.info("Order removed from hold", order_id=order_id)
