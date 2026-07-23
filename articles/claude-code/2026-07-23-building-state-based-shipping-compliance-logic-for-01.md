---
id: "2026-07-23-building-state-based-shipping-compliance-logic-for-01"
title: "Building State-Based Shipping Compliance Logic for Hemp E-Commerce on WooCommerce"
url: "https://qiita.com/quintecbd/items/c0365c676d4cfc4c6a9f"
source: "qiita"
category: "claude-code"
tags: ["MCP", "qiita"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

The problem

Most WooCommerce shipping restriction plugins are built around a simple assumption: pick a country, maybe a state, block or allow. That model works fine for general e-commerce, but it falls apart fast for hemp-derived cannabinoid products in the US, where legality is not a store-level setting. It is a per-product, per-state, per-cannabinoid-type problem, and the legal list changes over time as states pass new restrictions.

While building QuinteCBD (https://quintecbd.com), a hemp/cannabinoid store selling Delta 8, Delta 9, THCa, and CBD products, this was one of the first hard technical problems to solve. A single generic "restricted states" list at the store level does not work, because:

Delta 8 is restricted in far more states than Delta 9
THCa flower has its own separate restricted list, different again from Delta 8
A product can be legal in a state today and restricted next quarter, since state hemp law changes frequently
The restriction has to be visible and enforced before checkout, not discovered after payment

This article walks through the approach used to solve this at the product level, and some of the tooling decisions behind it.

Why store-level restriction plugins fail

Standard WooCommerce shipping zone restrictions work at the zone or method level. You can say "do not ship this shipping method to California," but that logic is not product-aware. If your catalog has 40 SKUs and each cannabinoid type has a different legal map across US states, a single shipping-zone rule cannot express that.

The practical result on QuinteCBD: a Delta 9 Pomegranate Gummy might be blocked from shipping to Alaska, California, Colorado, Hawaii, Idaho, Massachusetts, Montana, Oregon, Pennsylvania, South Dakota, Vermont, and Washington, while a Delta 8 Pomegranate Gummy on the same store has a completely different blocked list: California, Colorado, Delaware, Idaho, Iowa, Montana, Rhode Island, and Utah. Two products, same brand, same category, different legal maps.

The approach: product-level metadata plus checkout-time validation

The pattern that actually works is:

Store the restricted-state list as product metadata, not as a global setting. Each product carries its own array of blocked state codes as post meta (_restricted_states or similar custom field).
Surface it on the product page itself. Customers should see the restriction before they add to cart, not discover it at checkout. On QuinteCBD this renders as a plain notice block on the product page listing the exact states the product cannot ship to.
Validate again at checkout, keyed off the shipping address state, cross-referenced against every restricted product in the cart. This has to run as a blocking validation hook (woocommerce_after_checkout_validation or equivalent), not just a display warning, because customers do sometimes ignore product-page notices.
Fail loud, not silent. If a customer's cart contains a product restricted in their shipping state, checkout should hard-block with a specific per-product message, not a generic "shipping unavailable" error that leaves them unsure which item caused it.
Why this can't be a "set once and forget" system

The part that trips people up building this for the first time: the restricted-state lists are not static data. US state-level hemp law, especially around Delta 8 and THCa, has shifted meaningfully over the past few years, and federal rule changes (like the compliance deadlines under recent Farm Bill-related legislation) can force a re-audit of every product's shipping map on short notice.

That means the metadata needs to be:

Easy to bulk-audit and update across the whole catalog, not buried in 40 individual product edit screens
Versioned or at least timestamped, so you know when a given product's restricted list was last verified
Decoupled from the product description content, so legal team updates don't require a content rewrite

In practice, this pushed toward managing the restricted-state data as structured data (a maintained spreadsheet mapped to product IDs) rather than hand-editing each product in wp-admin, then syncing it in during content updates. It is a boring solution, but boring and auditable beats clever and unmaintainable when the cost of a mistake is a compliance violation.

Tooling note

For the WordPress/WooCommerce development work itself, this was built using MCP-based tooling connected directly to Claude, specifically a WordPress MCP server wired into the site, rather than manually hopping between wp-admin and a code editor for every content and metadata change. For a catalog-heavy compliance problem like this, being able to describe the desired product-level restriction logic in natural language and have it reflected directly into the CMS materially speeds up the audit-and-update cycle described above.

Takeaways for anyone building similar logic

If you are building any e-commerce store with product-level legal or regulatory restrictions, whether that is cannabinoids, age-restricted goods, or export-controlled items, the same shape of solution applies:

Do not model the restriction as a store-wide or shipping-zone-wide rule if the underlying legal reality is per-product
Surface restrictions before checkout, not just as a checkout-time block
Keep the restriction data structured and separately maintainable from the product content
Treat the legal map as something that needs periodic re-verification, not a one-time setup task

Hemp e-commerce is a fairly niche corner of WooCommerce development, but the underlying problem, per-item regulatory logic layered on top of a generic e-commerce platform, shows up anywhere a product catalog intersects with jurisdiction-specific law.
