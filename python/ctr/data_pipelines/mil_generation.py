from pyspark.sql.functions import col, to_date, lit
from data_pipelines.utils import get_spark_session
import data_pipelines.config as cfg
import os

def run_mil_generation():
    spark = get_spark_session("MILGeneration")
    
    print("Reading Canonical Transactions...")
    tx_df = spark.read.parquet(cfg.CANONICAL_TRANSACTIONS)
    
    # MIL Definition: Cash purchase of a monetary instrument between $3,000 and $10,000 inclusive
    mil_df = tx_df.filter(
        (col("is_cash") == True) & 
        (col("transaction_type") == "MONETARY_INSTRUMENT_PURCHASE") &
        (col("amount") >= 3000.0) &
        (col("amount") <= 10000.0)
    )
    
    print("Enriching with Customer Metadata...")
    customers_df = spark.read.parquet(cfg.CANONICAL_CUSTOMERS)
    non_customers_df = spark.read.parquet(cfg.CANONICAL_NON_CUSTOMERS)
    universal_entities_df = customers_df.unionByName(non_customers_df, allowMissingColumns=True)
    
    # Join on conductor_id since they are the ones purchasing the MIL
    mil_df = mil_df.join(universal_entities_df, mil_df.conductor_id == universal_entities_df.customer_id, "inner")
    
    # Select columns of interest for the log
    mil_df = mil_df.select(
        col("transaction_id"),
        col("timestamp"),
        col("amount"),
        col("location_id"),
        col("conductor_id").alias("purchaser_id"),
        col("first_name"),
        col("last_name"),
        col("tin"),
        col("address"),
        col("city"),
        col("state")
    )
    
    print(f"Writing {mil_df.count()} MIL Records to Canonical Store...")
    mil_df.write.mode("overwrite").parquet(cfg.CANONICAL_MILS)
    
    print("MIL Generation complete.")
    spark.stop()

if __name__ == "__main__":
    run_mil_generation()
