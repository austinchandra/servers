import json
from datetime import datetime
from lib.db import Database
from lib.types import OrderStatus, Shipment
import os
from dotenv import load_dotenv

load_dotenv()

db = Database(url=os.getenv("DATABASE_URL"))

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
        print(f"Order {order_id} not found")
        return

    # Add the new shipment
    db.upsert_shipment(Shipment(
        order_id=order_id,
        shipment_id=shipment_data["id"],
        tracking_url=shipment_data.get("tracking_url"),
    ))

    # Mark as partial unless Printful says fully fulfilled
    printful_status = order_data.get("status")
    new_status = OrderStatus.fulfilled if printful_status == "fulfilled" else OrderStatus.partial
    db.update_order(order_id, status=new_status, updated_at=datetime.now())


def handle_order_fulfilled(data: dict):
    order_id = int(data["order"]["external_id"])
    db.update_order(order_id, status=OrderStatus.fulfilled, updated_at=datetime.now())


def handle_order_failed(data: dict):
    order_id = int(data["order"]["external_id"])
    db.update_order(order_id, status=OrderStatus.failed, updated_at=datetime.now())

def handle_order_put_hold(data: dict):
    # Order is on hold but still pending from our perspective
    order_id = int(data["order"]["external_id"])
    print("order:", order_id, " is put on hold")


def handle_order_remove_hold(data: dict):
    # Order is back in processing
    order_id = int(data["order"]["external_id"])
    print("order:", order_id, " is removed from hold")
