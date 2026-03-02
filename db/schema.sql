-- These order statuses reflect the options on Printful. Before sending it to Printful, the status
-- will be NULL.

-- Failed - Order Placement Failed
-- Pending - Order Sent for Fulfillment
-- Partial - Some Items Shipped
-- Fulfilled - All Items Shipped
CREATE TYPE order_status AS ENUM (
  'failed',
  'pending',
  'partial',
  'fulfilled',
);

CREATE TABLE orders (
  -- Use a unique integer ID for easy lookups.
  id                SERIAL PRIMARY KEY,

  -- Store the customer email and order status.
  email             TEXT NOT NULL,
  status            order_status,

  -- References to the same order in Stripe and Printful.
  stripe_id         TEXT UNIQUE NOT NULL,
  printful_id       TEXT,

  -- Dates for when this object is updated or created.
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- The URL of the Stripe receipt, and the tracking link, when available.
  receipt_url       TEXT NOT NULL,
  tracking_url      TEXT,

  -- The price the user pays, and my own cost.
  price             INTEGER NOT NULL,
  cost              INTEGER
);

CREATE TABLE shipments (
  -- Use a reference to orders.
  order_id      INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  -- Store a Printful shipment ID.
  shipment_id   INTEGER NOT NULL,
  -- Hopefully this URL works!
  tracking_url  TEXT,
  PRIMARY KEY (order_id, shipment_id)
);

CREATE TABLE order_items (
  -- Use a foreign key reference for lookups
  order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  -- Store the Printful product ID, which differentiates across sizes.
  product_id  TEXT NOT NULL,
  -- How many of this item did the user purchase?
  quantity    INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE stripe_checkouts (
  -- The Stripe checkout session used for idempotency protection
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);