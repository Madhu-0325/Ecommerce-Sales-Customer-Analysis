-- =============================================
-- E-Commerce Sales Analysis SQL Queries
-- =============================================

-- 1. Overall KPIs
SELECT
    COUNT(*) AS total_sessions,
    SUM(purchased) AS total_purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate_pct,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(CASE WHEN purchased = 1 THEN revenue END), 2) AS avg_order_value
FROM ecommerce_sales;

-- 2. Revenue by Product Category
SELECT
    product_category,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(CASE WHEN purchased = 1 THEN revenue END), 2) AS avg_order_value
FROM ecommerce_sales
GROUP BY product_category
ORDER BY total_revenue DESC;

-- 3. Conversion Rate by Marketing Channel
SELECT
    marketing_channel,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue
FROM ecommerce_sales
GROUP BY marketing_channel
ORDER BY conversion_rate DESC;

-- 4. Cart Abandonment Analysis
SELECT
    product_category,
    SUM(added_to_cart) AS added_to_cart,
    SUM(cart_abandoned) AS abandoned,
    ROUND(SUM(cart_abandoned) * 100.0 / NULLIF(SUM(added_to_cart), 0), 2) AS abandon_rate_pct
FROM ecommerce_sales
GROUP BY product_category
ORDER BY abandon_rate_pct DESC;

-- 5. Device Performance
SELECT
    device_type,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(time_on_site_sec), 0) AS avg_time_on_site
FROM ecommerce_sales
GROUP BY device_type
ORDER BY total_revenue DESC;

-- 6. Seasonal Trends
SELECT
    visit_season,
    visit_month,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue
FROM ecommerce_sales
GROUP BY visit_season, visit_month
ORDER BY visit_month;

-- 7. Discount Impact
SELECT
    discount_percent,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    ROUND(AVG(CASE WHEN purchased = 1 THEN revenue END), 2) AS avg_order_value
FROM ecommerce_sales
GROUP BY discount_percent
ORDER BY discount_percent;

-- 8. Customer Lifetime Value (Top Customers)
SELECT
    customer_id,
    COUNT(*) AS total_sessions,
    SUM(purchased) AS total_purchases,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(CASE WHEN purchased = 1 THEN revenue END), 2) AS avg_order_value,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate
FROM ecommerce_sales
GROUP BY customer_id
HAVING SUM(purchased) >= 2
ORDER BY total_revenue DESC
LIMIT 20;

-- 9. New vs Returning Customer Comparison
SELECT
    user_type,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(pages_viewed), 1) AS avg_pages_viewed,
    ROUND(AVG(time_on_site_sec), 0) AS avg_time_on_site
FROM ecommerce_sales
GROUP BY user_type;

-- 10. Payment Method Analysis
SELECT
    payment_method,
    COUNT(*) AS sessions,
    SUM(purchased) AS purchases,
    ROUND(SUM(purchased) * 100.0 / COUNT(*), 2) AS conversion_rate,
    SUM(revenue) AS total_revenue
FROM ecommerce_sales
GROUP BY payment_method
ORDER BY total_revenue DESC;
