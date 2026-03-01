This repository contains the "server" logic for my clothing brand, a personal line of five pieces hosted on [achandra.io](https://achandra.io),
designed to last across time, and for wear in the office, at home, or in the gym.

Each piece represents a certain "feeling" or idea, and I wear them daily, choosing the item based on my mood, but enough about the clothes!,
and you came here for the servers, so let us chat technical architecture.

---

### Architecture

Each order goes in through Stripe, and on my "checkout" page, I send a request to my backend to create a "checkout service" link, a customized
checkout page containing the exact products the user desires.

I listen to purchases on Stripe with a webhook, an AWS Lambda function, and with each request, I add an entry to my database, a PostgresQL
instance running on AWS AuroraDSQL, a distributed SQL database covered in their generous free tier.

What happens if AWS is down and my webhook request fails?—then, I use AWS EventBridge and a second Lambda function to operate as a "cron job,"
and this runs periodically to trigger a "catch-up" request, in which I query against the REST API for any orders I may have missed.

Once I add an entry to my database, I send a request to Printful, who fulfill my orders—and they do an excellent job—and I listen to order
updates the same way, using a webhook to update my status on changes, such that my database reflects the source of truth.

In the same manner, I listen to these using a Lambda function, with a second EventBridge set up to query against the Printful REST API, in case
there are any order updates I miss.

Lastly, to tie everything together, I have a "recovery" job, and this runs on each startup, checking the Printful API against my database, and
the Stripe API against my database, and making sure I did not miss any orders, or to catch, for instance, fraudulent requests—supposing someone
steals my API key!

---

### Metrics

So, no application is complete without monitoring, although—in my opinion—it may be complete without tests, and I dislike "test-driven-development,"
and I prefer another TDD in the form of "thought-driven-development."

Therefore, I setup AWS with its "Cloud Watch" metrics, the only item, alas, not included on the generous free tier, such that I may rack up a bill,
according to Claude, of just under a dollar a month, which I find acceptable, and the other services charge only per-order, and this, too, do I find
acceptable.

I connect these with AWS "simple notification service," such that if someone gets away with my keys, I get a text immediately, and if I have too many
errors, I get emails and alerted in this manner, so I can keep things running smoothly.

I make some bold claims and promises!—and for instance, I say there is "no customer service," and people must have the "courage" to order from my site,
and if they get the wrong item, so be it!

What, as though I have time to deal with all of that, but if they order, and it does *not* go through, then that is my responsibility, so therefore I
draw the line and hold it true.

---

Test in production!—and why not, and the last service I forgot to mention is "simple queueing service," which I plan to use to store incoming requests,
before I run my Lambda against them, just as a safety guard, a recommendation from a smart friend of mine, along with many other technical decisions in
this stack, and life goes better with a touch of good advice!
