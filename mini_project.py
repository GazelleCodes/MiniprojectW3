import pandas as pd
# Q1. Data Ingestion Pipeline 
# 1. Read all datasets.  

clickstream_df = pd.read_csv("clickstream.csv")
customers_df = pd.read_csv("customers.csv")
orders_df = pd.read_csv("orders.csv")
products_df = pd.read_csv("products.csv")

# 2. Validate schema consistency.  

'''
I validated the expected column names and column order for all four datasets: customers, clickstream, orders, and products.
All four datasets passed the schema check. 
I also checked for missing values across all datasets. 
Missing values were found only in the clickstream dataset, affecting customer_id (60), page_url (83), and device_type (424). 
The other three datasets contained no missing values.
'''
# Checking to see all columns are present
# print(customers_df.columns)
# print(clickstream_df.columns)
# print(orders_df.columns)
# print(products_df.columns)


# Check to see if data types are correct
# print(customers_df.dtypes)
# print(clickstream_df.dtypes)
# print(orders_df.dtypes)
# print(products_df.dtypes)


#Check whether the columns match our expectations
# Define the expected columns for each dataset
expected_schemas = {
    "customers": [
        "customer_id", "customer_name", "email", "city", "signup_date"
    ],
    "clickstream": [
        "event_id", "customer_id", "event_type",
        "page_url", "event_timestamp", "device_type"
    ],
    "orders": [
        "order_id", "customer_id", "product_id", "order_date",
        "quantity", "unit_price", "payment_status"
    ],
    "products": [
        "product_id", "product_name", "category",
        "supplier_id", "cost_price", "selling_price"
    ]
}

# Match each dataset to its expected schema
datasets = {
    "customers": customers_df,
    "clickstream": clickstream_df,
    "orders": orders_df,
    "products": products_df
}

# Validate each dataset
# for name, df in datasets.items():
#     actual_columns = df.columns.tolist()
#     expected_columns = expected_schemas[name]

#     # if actual_columns == expected_columns:
#     #     print(f"{name}: Schema is valid")
#     # else:
#     #     print(f"{name}: Schema is INVALID")

#         missing_columns = [
#             col for col in expected_columns
#             if col not in actual_columns
#         ]

#         unexpected_columns = [
#             col for col in actual_columns
#             if col not in expected_columns
#         ]

        # print("Missing columns:", missing_columns)
        # print("Unexpected columns:", unexpected_columns)


# Checking missing values in all datasets
for name, df in datasets.items():
    missing = df.isna().sum()
    missing = missing[missing > 0]

    # print(f"\n{name.upper()}")

    # if missing.empty:
    #     print("No missing values")
    # else:
    #     print(missing)

# 3. Detect duplicate customers. 
# print("Total customer rows:", len(customers_df))
# print("Duplicate customer IDs:", customers_df["customer_id"].duplicated().sum())
# print("Duplicate customer records:", customers_df.duplicated().sum())

# Check customer emails
invalid_emails = ~customers_df["email"].str.contains("@", na=False)

# Check signup dates
invalid_dates = pd.to_datetime(
    customers_df["signup_date"], errors="coerce"
).isna()

# Report both checks together
# print("Invalid emails:", invalid_emails.sum())
# print("Invalid signup dates:", invalid_dates.sum())

# Q2. Data Cleaning & Transformation 
# 1. Standardize city names. (if any)  

customers_df["city"] = (
    customers_df["city"]
    .str.strip()
    .str.title()
)

# print(customers_df["city"].unique())

# 2. Convert timestamps correctly.  (if any)

# check for date data types
# print("Customer signup dates:")
# print(customers_df["signup_date"].head())

# print("\nClickstream event timestamps:")
# print(clickstream_df["event_timestamp"].head())

# print("\nOrder dates:")
# print(orders_df["order_date"].head())

# converting the date
customers_df["signup_date"] = pd.to_datetime(
    customers_df["signup_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

# print(customers_df["signup_date"].dtype)
# print(orders_df["order_date"].dtype)

# print("Invalid signup dates:", customers_df["signup_date"].isna().sum())
# print("Invalid order dates:", orders_df["order_date"].isna().sum())

clickstream_raw = pd.read_csv("clickstream.csv")

# # Read the original timestamp strings so we don't parse already-converted values
timestamps = clickstream_raw["event_timestamp"].astype("string")

# Identify timestamps that start with year-month-day, such as 2025-02-05
iso_mask = timestamps.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)

# Create an empty datetime column with UTC timezone
parsed_timestamps = pd.Series(
    pd.NaT,
    index=timestamps.index,
    dtype="datetime64[us, UTC]"
)

# Parse ISO-style dates without changing their month and day
parsed_timestamps.loc[iso_mask] = pd.to_datetime(
    timestamps.loc[iso_mask],
    format="mixed",
    utc=True,
    errors="coerce"
)

# Parse slash-separated dates using day/month/year
parsed_timestamps.loc[~iso_mask] = pd.to_datetime(
    timestamps.loc[~iso_mask],
    format="mixed",
    dayfirst=True,
    utc=True,
    errors="coerce"
)

# Save the corrected timestamps to the working DataFrame
clickstream_df["event_timestamp"] = parsed_timestamps

# Check the conversion results
# print("Invalid timestamps:", parsed_timestamps.isna().sum())
# print(parsed_timestamps.head(10))

# 3. Handle missing values.  (if any)
# Store the datasets we want to check in one dictionary

datasets = {
    "customers": customers_df,
    "clickstream": clickstream_df,
    "orders": orders_df,
    "products": products_df
}

# Count missing values in each dataset
for name, df in datasets.items():
    # print(f"\n{name.upper()}")

    # Count missing values in each column
    missing_values = df.isna().sum()

    # Display only columns that contain missing values
    # print(missing_values[missing_values > 0])

# Replace missing device types with "Unknown"
clickstream_df["device_type"] = clickstream_df["device_type"].fillna("Unknown")

# Count any remaining missing device types
# print(
#     "Missing device types:",
#     clickstream_df["device_type"].isna().sum()
# )

# # Check how many events now have each device type
# print(clickstream_df["device_type"].value_counts())

# Convert device types to lowercase and remove extra spaces
clickstream_df["device_type"] = (
    clickstream_df["device_type"]
    .str.strip()
    .str.lower()
)

# Check the standardized device type counts
# print(clickstream_df["device_type"].value_counts())

# Count remaining missing values in the two columns
# print("Missing customer IDs:", clickstream_df["customer_id"].isna().sum())
# print("Missing page URLs:", clickstream_df["page_url"].isna().sum())


# 4. Remove corrupted rows.

# Identify clickstream rows with missing customer_id or page_url
invalid_mask = (
    clickstream_df["customer_id"].isna()
    | clickstream_df["page_url"].isna()
)

# Store corrupted/incomplete rows separately for review
rejected_clickstream = clickstream_df[invalid_mask].copy()

# Keep only rows with both customer_id and page_url present
clean_clickstream = clickstream_df[~invalid_mask].copy()

# Display how many rows were retained and rejected
# print("Original rows:", len(clickstream_df))
# print("Rejected rows:", len(rejected_clickstream))
# print("Clean rows:", len(clean_clickstream))


# Q3. Clickstream Analytics 
# 1. Find the most visited pages.  

# Count how many times each page appears
page_visits = clean_clickstream["page_url"].value_counts()

# Display the 10 most visited pages
# print("Top 10 most visited pages:")
# print(page_visits.head(10))


# 2. Calculate session counts.
# Count the number of unique customers in the cleaned clickstream data
unique_customers = clean_clickstream["customer_id"].nunique()

# Count the total number of retained clickstream events
total_events = len(clean_clickstream)

# Display the counts
# print("Unique customers:", unique_customers)
# print("Total events:", total_events)


# 2. Calculate session counts.
'''
Since the dataset did not contain a session ID, sessions were estimated using a 30-minute inactivity threshold. 
Events were sorted by customer and timestamp, and a new session was counted whenever a customer’s first event occurred or more than 30 minutes had passed since their previous event. 
This identified 1,854 sessions across 100 unique customers in the cleaned clickstream data.
'''

# Sort events by customer and timestamp
sessions_df = clean_clickstream.sort_values(
    ["customer_id", "event_timestamp"]
).copy()

# Calculate the time since each customer's previous event
sessions_df["time_since_previous"] = (
    sessions_df.groupby("customer_id")["event_timestamp"].diff()
)

# Start a new session if this is the customer's first event
# or if more than 30 minutes have passed since their previous event
sessions_df["new_session"] = (
    sessions_df["time_since_previous"].isna()
    | (sessions_df["time_since_previous"] > pd.Timedelta(minutes=30))
)

# Count the sessions across all customers
total_sessions = sessions_df["new_session"].sum()

# Count sessions for each customer
sessions_per_customer = sessions_df.groupby("customer_id")["new_session"].sum()

# Display the results
# print("Total sessions:", total_sessions)
# print("\nSessions per customer:")
# print(sessions_per_customer)


# 3. Find mobile vs desktop traffic percentage. 

# Keep only events from mobile and desktop devices
mobile_desktop = clean_clickstream[
    clean_clickstream["device_type"].isin(["mobile", "desktop"])
]

# Count the events for each device type
device_counts = mobile_desktop["device_type"].value_counts()

# Calculate the total mobile and desktop events
total_mobile_desktop = device_counts.sum()

# Calculate the percentage for each device type
device_percentages = (device_counts / total_mobile_desktop) * 100

# Display the counts and percentages
print("Event counts:")
print(device_counts)

print("\nTraffic percentages:")
print(device_percentages.round(2))
