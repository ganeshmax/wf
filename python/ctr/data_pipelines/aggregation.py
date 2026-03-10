from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum as _sum, expr
from data_pipelines.utils import get_spark_session
import data_pipelines.config as cfg
import os

def run_aggregation():
    spark = get_spark_session("CTRAggregation")
        
    print("Reading Canonical Transactions & Account Owners...")
    # We only care about cash transactions for CTRs
    tx_df = spark.read.parquet(cfg.CANONICAL_TRANSACTIONS).filter(col("is_cash") == True)
    owners_df = spark.read.parquet(cfg.CANONICAL_ACCOUNT_OWNERS)
    
    # Map Business Days: Saturday (7) -> Monday, Sunday (1) -> Monday
    # Day of week function in PySpark returns 1 (Sunday) to 7 (Saturday)
    tx_df = tx_df.withColumn("raw_date", to_date(col("timestamp")))
    tx_df = tx_df.withColumn(
        "date",
        expr(
            "CASE " +
            "WHEN dayofweek(raw_date) = 7 THEN date_add(raw_date, 2) " + # Saturday + 2 days = Monday
            "WHEN dayofweek(raw_date) = 1 THEN date_add(raw_date, 1) " + # Sunday + 1 day = Monday
            "ELSE raw_date END"
        )
    )
    
    # -------------------------------------------------------------
    # JOINT ACCOUNT EXPLOSION JOIN
    # -------------------------------------------------------------
    # Instead of aggregating directly on `account_id`, we join against ALL owners of that account.
    # If John and Mary share a Checking Account, a single $11,000 tx row here becomes TWO $11,000 tx rows, 
    # one mapping to John as beneficiary and one mapping to Mary as beneficiary!
    # -------------------------------------------------------------
    tx_with_owners_df = tx_df.join(owners_df, "account_id", "inner") \
                             .withColumnRenamed("customer_id", "beneficiary_id")
    
    # Separate by direction
    cash_in_df = tx_with_owners_df.filter(col("transaction_type") == "DEPOSIT")
    cash_out_df = tx_with_owners_df.filter(col("transaction_type") == "WITHDRAWAL")
    
    print("Writing 4 Distinct Aggregations...")
    # 1. Beneficiary Cash-In
    ben_in = cash_in_df.groupBy("beneficiary_id", "date").agg(_sum("amount").alias("total_amount"))
    ben_in.write.mode("overwrite").parquet(cfg.AGG_BEN_IN)
    
    # 2. Beneficiary Cash-Out
    ben_out = cash_out_df.groupBy("beneficiary_id", "date").agg(_sum("amount").alias("total_amount"))
    ben_out.write.mode("overwrite").parquet(cfg.AGG_BEN_OUT)
    
    # 3. Conductor Cash-In
    cond_in = cash_in_df.groupBy("conductor_id", "date").agg(_sum("amount").alias("total_amount"))
    cond_in.write.mode("overwrite").parquet(cfg.AGG_COND_IN)
    
    # 4. Conductor Cash-Out
    cond_out = cash_out_df.groupBy("conductor_id", "date").agg(_sum("amount").alias("total_amount"))
    cond_out.write.mode("overwrite").parquet(cfg.AGG_COND_OUT)
    
    print("4-Way Complex Aggregation complete.")
    spark.stop()

if __name__ == "__main__":
    run_aggregation()
