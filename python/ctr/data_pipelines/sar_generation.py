from pyspark.sql.functions import col, to_date, sum as _sum, count
from data_pipelines.utils import get_spark_session
import data_pipelines.config as cfg
import os

def run_sar_generation():
    spark = get_spark_session("SARGeneration")
    
    print("Reading Canonical Transactions...")
    tx_df = spark.read.parquet(cfg.CANONICAL_TRANSACTIONS)
    
    # Filter for Cash Deposits
    cash_deposits = tx_df.filter(
        (col("is_cash") == True) & 
        (col("transaction_type") == "DEPOSIT")
    ).withColumn("date", to_date(col("timestamp")))
    
    print("Aggregating Daily Deposits per Account...")
    daily_deposits = cash_deposits.groupBy("account_id", "date").agg(_sum("amount").alias("daily_amount"))
    
    # Structuring Rule: Multiple near-threshold deposits (> $9,000 and <= $10,000)
    suspicious_days = daily_deposits.filter(
        (col("daily_amount") > 9000.0) & 
        (col("daily_amount") <= 10000.0)
    )
    
    print("Detecting Structuring Patterns...")
    account_structuring = suspicious_days.groupBy("account_id").agg(
        count("date").alias("suspicious_days_count"), 
        _sum("daily_amount").alias("total_structured_amount")
    )
    
    # Trigger SAR if we see the pattern 2 or more times
    sar_alerts = account_structuring.filter(col("suspicious_days_count") >= 2)
    
    print("Resolving Account Owners for SAR Alerts...")
    owners_df = spark.read.parquet(cfg.CANONICAL_ACCOUNT_OWNERS)
    
    # Join to find ALL owners of the structured account
    sar_with_owners = sar_alerts.join(owners_df, "account_id", "inner")
    
    print("Enriching with Customer Metadata...")
    customers_df = spark.read.parquet(cfg.CANONICAL_CUSTOMERS)
    non_customers_df = spark.read.parquet(cfg.CANONICAL_NON_CUSTOMERS)
    universal_entities_df = customers_df.unionByName(non_customers_df, allowMissingColumns=True)
    
    # Join to get PII for the structured SARs
    sar_final_df = sar_with_owners.join(universal_entities_df, on="customer_id", how="inner")
                                  
    sar_final_df = sar_final_df.select(
        col("account_id"),
        col("total_structured_amount"),
        col("suspicious_days_count"),
        col("customer_id").alias("suspect_id"),
        col("first_name"),
        col("last_name"),
        col("tin"),
        col("address"),
        col("city"),
        col("state")
    )
    
    print(f"Writing {sar_final_df.count()} SAR Records to Canonical Store...")
    sar_final_df.write.mode("overwrite").parquet(cfg.CANONICAL_SARS)
    
    print("SAR Generation complete.")
    spark.stop()

if __name__ == "__main__":
    run_sar_generation()
