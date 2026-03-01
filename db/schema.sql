CREATE TYPE order_status AS ENUM (
  'pending',
  'placed',
  'fulfilled',
  'shipped',
  'delivered'
);

CREATE TABLE orders (
  -- Use a unique integer ID for easy lookups.
  id                SERIAL PRIMARY KEY,

  -- Store the customer email and order status.
  email             TEXT NOT NULL,
  status            order_status NOT NULL DEFAULT 'pending',

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

CREATE TABLE order_items (
  -- Use a foreign key reference for lookups
  order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  -- Store the Printful product ID, which differentiates across sizes.
  product_id  TEXT NOT NULL,
  -- How many of this item did the user purchase?
  quantity    INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (order_id, product_id)
);
