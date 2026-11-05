
USE ecommerce_db;



-- 0A. Show the tables in this database.
SHOW TABLES;

-- 0B. Check column names and data types before running analysis.
DESCRIBE ecommerce_sales;

-- 0C. Count the number of records/sessions imported.
SELECT COUNT(*) AS total_rows
FROM ecommerce_sales;

-- 0D. Preview the first 10 records.
SELECT *
FROM ecommerce_sales
LIMIT 10;


-- ============================================================
-- 1. OVERALL BUSINESS KPIs
-- Purpose: Summarize sessions, purchases, conversion rate, and revenue.
-- Assumptions: purchased = 1 means a purchase; purchased = 0 means no purchase.
-- revenue is the revenue value for each row/session.
-- ============================================================

SELECT
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue,
    ROUND(AVG(CASE WHEN purchased = 1 THEN revenue END), 2) AS avg_revenue_per_purchase_session
FROM ecommerce_sales;


-- ============================================================
-- 2. REVENUE BY PRODUCT CATEGORY
-- Purpose: Identify which product category contributes the most revenue.
-- Numeric category codes are shown as stored; map them to names only if you
-- have a reliable codebook/data dictionary.
-- ============================================================

SELECT
    product_category,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct
FROM ecommerce_sales
GROUP BY product_category
ORDER BY total_revenue DESC;


-- ============================================================
-- 3. MARKETING CHANNEL PERFORMANCE
-- Purpose: Compare traffic, purchases, conversion rate, and revenue by channel.
-- ============================================================

SELECT
    marketing_channel,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY marketing_channel
ORDER BY total_revenue DESC;


-- ============================================================
-- 4. CART ABANDONMENT ANALYSIS
-- Purpose: Calculate how many sessions added items to cart and how many
-- abandoned the cart.
-- Assumption: added_to_cart and cart_abandoned are binary flags (1/0).
-- The denominator is sessions where an item was added to cart.
-- ============================================================

SELECT
    SUM(CASE WHEN added_to_cart = 1 THEN 1 ELSE 0 END) AS sessions_with_cart_add,
    SUM(CASE WHEN added_to_cart = 1 AND cart_abandoned = 1 THEN 1 ELSE 0 END)
        AS abandoned_cart_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN added_to_cart = 1 AND cart_abandoned = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN added_to_cart = 1 THEN 1 ELSE 0 END), 0),
        2
    ) AS cart_abandonment_rate_pct
FROM ecommerce_sales;


-- ============================================================
-- 5. DEVICE TYPE PERFORMANCE
-- Purpose: Compare sessions, purchases, conversion rate, and revenue by device.
-- Numeric device codes are kept as stored until their meanings are confirmed.
-- ============================================================

SELECT
    device_type,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY device_type
ORDER BY conversion_rate_pct DESC;


-- ============================================================
-- 6. MONTHLY PERFORMANCE
-- Purpose: Track sessions, purchases, conversion rate, and revenue by month.
-- Uses visit_month, so no date-format conversion is required.
-- If visit_month is a numeric code, results will show that code.
-- ============================================================

SELECT
    visit_month,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY visit_month
ORDER BY visit_month;


-- ============================================================
-- 7. SEASONAL PERFORMANCE
-- Purpose: Compare customer activity and sales across seasons.
-- ============================================================

SELECT
    visit_season,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY visit_season
ORDER BY total_revenue DESC;


-- ============================================================
-- 8. DISCOUNT ANALYSIS
-- Purpose: Compare purchasing behavior across discount ranges.
-- This shows association, not proof that discounts caused purchases.
-- ============================================================

SELECT
    CASE
        WHEN discount_percent IS NULL THEN 'Unknown'
        WHEN discount_percent = 0 THEN '0% discount'
        WHEN discount_percent <= 10 THEN '1-10% discount'
        WHEN discount_percent <= 20 THEN '11-20% discount'
        ELSE 'Above 20% discount'
    END AS discount_band,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY discount_band
ORDER BY MIN(COALESCE(discount_percent, -1));


-- ============================================================
-- 9. TOP CUSTOMERS BY REVENUE
-- Purpose: Find customers with the highest recorded revenue.
-- Note: This is based only on records available in this dataset, not
-- necessarily true lifetime value across all historical purchases.
-- ============================================================

SELECT
    customer_id,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY customer_id
HAVING SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) > 0
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 10. NEW VS RETURNING CUSTOMER ANALYSIS
-- Purpose: Compare sessions, purchase sessions, conversion, and revenue by user type.
-- Numeric user_type codes are kept as stored until the code mapping is confirmed.
-- ============================================================

SELECT
    user_type,
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue,
    COUNT(DISTINCT customer_id) AS distinct_customers
FROM ecommerce_sales
GROUP BY user_type
ORDER BY total_revenue DESC;


-- ============================================================
-- 11. PAYMENT METHOD ANALYSIS
-- Purpose: Compare purchase activity and revenue by payment method.
-- If payment_method is only recorded for purchases, interpret session counts
-- accordingly. If the column does not exist, remove this query or check schema.
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS total_records,
    SUM(CASE WHEN purchased = 1 THEN 1 ELSE 0 END) AS purchase_sessions,
    ROUND(SUM(COALESCE(revenue, 0)), 2) AS total_revenue
FROM ecommerce_sales
GROUP BY payment_method
ORDER BY total_revenue DESC;


-- ============================================================
-- 12. CUSTOMER ENGAGEMENT: TIME ON SITE
-- Purpose: Compare average time on site for purchase and non-purchase sessions.
-- Assumes time_on_site_sec is measured in seconds.
-- ============================================================

SELECT
    purchased,
    COUNT(*) AS total_sessions,
    ROUND(AVG(time_on_site_sec), 2) AS avg_time_on_site_sec,
    ROUND(AVG(time_on_site_sec) / 60.0, 2) AS avg_time_on_site_min
FROM ecommerce_sales
GROUP BY purchased
ORDER BY purchased;


-- ============================================================
-- 13. CUSTOMER ENGAGEMENT: PAGES VIEWED
-- Purpose: Compare average pages viewed by purchase outcome.
-- ============================================================

SELECT
    purchased,
    COUNT(*) AS total_sessions,
    ROUND(AVG(pages_viewed), 2) AS avg_pages_viewed
FROM ecommerce_sales
GROUP BY purchased
ORDER BY purchased;


-- ============================================================
-- 14. PRODUCT QUANTITY AND UNIT PRICE SUMMARY
-- Purpose: Summarize the recorded unit prices and quantities.
-- This is a descriptive check; it does not replace revenue if revenue is
-- already defined in the dataset.
-- ============================================================

SELECT
    COUNT(*) AS total_records,
    ROUND(MIN(unit_price), 2) AS minimum_unit_price,
    ROUND(AVG(unit_price), 2) AS average_unit_price,
    ROUND(MAX(unit_price), 2) AS maximum_unit_price,
    SUM(quantity) AS total_quantity_recorded,
    ROUND(AVG(quantity), 2) AS average_quantity_per_record
FROM ecommerce_sales;


-- ============================================================
-- 15. DATA QUALITY CHECKS
-- Purpose: Find missing values in important fields and check purchase flags.
-- ============================================================

SELECT
    SUM(customer_id IS NULL) AS missing_customer_id,
    SUM(session_id IS NULL) AS missing_session_id,
    SUM(visit_date IS NULL) AS missing_visit_date,
    SUM(purchased IS NULL) AS missing_purchased,
    SUM(revenue IS NULL) AS missing_revenue,
    SUM(product_category IS NULL) AS missing_product_category
FROM ecommerce_sales;

-- Check the values stored in the purchase flag.
SELECT
    purchased,
    COUNT(*) AS record_count
FROM ecommerce_sales
GROUP BY purchased
ORDER BY purchased;

-- Check for duplicate session IDs.
-- If session_id is expected to be unique, any returned row indicates a duplicate.
SELECT
    session_id,
    COUNT(*) AS records_per_session
FROM ecommerce_sales
GROUP BY session_id
HAVING COUNT(*) > 1
ORDER BY records_per_session DESC
LIMIT 20;
