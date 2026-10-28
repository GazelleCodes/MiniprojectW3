USE sales_db;

SHOW TABLES;
SELECT* FROM orders

SELECT COUNT(*) FROM customers;

-- Q1. Intermediate SQL Queries 
-- 1. Find top 10 customers by revenue.  

SELECT
    c.customer_id,
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Find month-over-month sales growth.

WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
        SUM(quantity * unit_price) AS total_sales
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
),
sales_with_previous AS (
    SELECT
        sales_month,
        total_sales,
        LAG(total_sales) OVER (
            ORDER BY sales_month
        ) AS previous_month_sales
    FROM monthly_sales
)
SELECT
    sales_month,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(previous_month_sales, 2) AS previous_month_sales,
    ROUND(
        (total_sales - previous_month_sales)
        / NULLIF(previous_month_sales, 0) * 100,
        2
    ) AS mom_growth_percentage
FROM sales_with_previous
ORDER BY sales_month;

-- 3. Find customers who ordered in consecutive months. 

SELECT DISTINCT
    a.customer_id,
    DATE_FORMAT(a.order_date, '%Y-%m') AS first_month,
    DATE_FORMAT(b.order_date, '%Y-%m') AS next_month
FROM orders a
JOIN orders b
    ON a.customer_id = b.customer_id
    AND YEAR(b.order_date) * 12 + MONTH(b.order_date)
        = YEAR(a.order_date) * 12 + MONTH(a.order_date) + 1
ORDER BY a.customer_id, first_month;

-- 4. Find products never ordered.  

SELECT p.*
FROM products p
LEFT JOIN orders o
    ON p.product_id = o.product_id
WHERE o.product_id IS NULL;
-- “No products were found that had never been ordered. 
-- All products in the products table have at least one matching order.”

-- 5. Find revenue contribution percentage by category.  
-- What percentage of total sales comes from each product category.


SELECT
    p.category,
    ROUND(SUM(o.quantity * o.unit_price), 2) AS category_revenue,
    ROUND(
        SUM(o.quantity * o.unit_price) * 100
        / (SELECT SUM(quantity * unit_price) FROM orders),
        2
    ) AS revenue_percentage
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue_percentage DESC;

-- Q2. Advanced SQL
-- 1. Rank customers based on total revenue.  

SELECT
    customer_id,
    total_revenue,
    RANK() OVER (ORDER BY total_revenue DESC) AS customer_rank
FROM (
    SELECT
        customer_id,
        SUM(quantity * unit_price) AS total_revenue
    FROM orders
    GROUP BY customer_id
) AS customer_sales
ORDER BY customer_rank;

-- 2. Find running total sales by month.


SELECT
    sales_month,
    monthly_sales,
    SUM(monthly_sales) OVER (
        ORDER BY sales_month
    ) AS running_total
FROM (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
        SUM(quantity * unit_price) AS monthly_sales
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
) AS monthly
ORDER BY sales_month;

-- 3. Find the highest selling product per category.  

WITH product_sales AS (
    SELECT
        p.category,
        p.product_id,
        SUM(o.quantity) AS total_quantity_sold
    FROM products p
    JOIN orders o
        ON p.product_id = o.product_id
    GROUP BY p.category, p.product_id
),
ranked_products AS (
    SELECT
        category,
        product_id,
        total_quantity_sold,
        RANK() OVER (
            PARTITION BY category
            ORDER BY total_quantity_sold DESC
        ) AS product_rank
    FROM product_sales
)
SELECT
    category,
    product_id,
    total_quantity_sold
FROM ranked_products
WHERE product_rank = 1
ORDER BY category;

-- 4. Find 7-day rolling average sales.  

WITH daily_sales AS (
    SELECT
        DATE(order_date) AS sales_date,
        SUM(quantity * unit_price) AS total_sales
    FROM orders
    GROUP BY DATE(order_date)
)
SELECT
    sales_date,
    total_sales,
    ROUND(
        AVG(total_sales) OVER (
            ORDER BY sales_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_7_day_average
FROM daily_sales
ORDER BY sales_date;


/*Q3. SQL Optimization Scenario 
The following query takes 18 minutes: */
SELECT c.customer_name, 
 SUM(o.quantity * o.unit_price) 
FROM orders o 
JOIN customers c 
ON o.customer_id = c.customer_id
WHERE order_date >= '2025-01-01' 
GROUP BY c.customer_name; 

-- 1. Identify possible bottlenecks.  
/*
Bottleneck 1: Too many orders to check
MySQL may scan a large number of rows to find orders from January 1, 2025, onward.

Bottleneck 2: Joining two tables
MySQL must match each relevant order to its customer. This can be slow if the join columns aren't indexed.

Bottleneck 3: Grouping customers
MySQL must group orders by customer name and add up their revenue. With lots of rows, this can require extra work and memory.*/

-- 2. Suggest indexes.  
/* Create an index on orders(order_date) and orders(customer_id). 
Ensure customers(customer_id) is indexed, usually as a primary key.
*/
CREATE INDEX idx_orders_order_date
ON orders(order_date);

CREATE INDEX idx_orders_customer_id
ON orders(customer_id);

-- 3. Explain execution plan analysis.  

EXPLAIN
SELECT
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
WHERE o.order_date >= '2025-01-01'
GROUP BY  c.customer_id, c.customer_name;
/*
Use EXPLAIN to inspect access types, chosen indexes, estimated rows, and extra operations. 
Use EXPLAIN ANALYZE when supported to measure actual execution performance.
*/

/*Q4. Database Design 
Design schema for: 
*/









 