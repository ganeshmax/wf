from pyspark.sql.types import StructType, StructField, StringType, BooleanType, DoubleType

TRANSACTIONS_SCHEMA = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("account_id", StringType(), True),
    StructField("conductor_id", StringType(), True),
    StructField("location_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("is_cash", BooleanType(), True),
    StructField("currency", StringType(), True)
])

# For inferSchema files, we don't strictly need to declare them, but we can build more explicit schemas here if needed over time.
