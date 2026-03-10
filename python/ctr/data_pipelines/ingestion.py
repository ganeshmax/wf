from pyspark.sql import SparkSession
from data_pipelines.utils import get_spark_session
from data_pipelines.schemas import TRANSACTIONS_SCHEMA
import data_pipelines.config as cfg

def run_ingestion():
    spark = get_spark_session("CTRIngestion")
        
    print("Ingesting Customers...")
    customers_df = spark.read.csv(cfg.RAW_CUSTOMERS, header=True, inferSchema=True)
    customers_df.write.mode("overwrite").parquet(cfg.CANONICAL_CUSTOMERS)
    
    print("Ingesting Non-Customers...")
    non_customers_df = spark.read.csv(cfg.RAW_NON_CUSTOMERS, header=True, inferSchema=True)
    non_customers_df.write.mode("overwrite").parquet(cfg.CANONICAL_NON_CUSTOMERS)
    
    print("Ingesting Locations...")
    locations_df = spark.read.csv(cfg.RAW_LOCATIONS, header=True, inferSchema=True)
    locations_df.write.mode("overwrite").parquet(cfg.CANONICAL_LOCATIONS)
    
    print("Ingesting Accounts & Owners...")
    accounts_df = spark.read.csv(cfg.RAW_ACCOUNTS, header=True, inferSchema=True)
    accounts_df.write.mode("overwrite").parquet(cfg.CANONICAL_ACCOUNTS)
    account_owners_df = spark.read.csv(cfg.RAW_ACCOUNT_OWNERS, header=True, inferSchema=True)
    account_owners_df.write.mode("overwrite").parquet(cfg.CANONICAL_ACCOUNT_OWNERS)
    
    print("Ingesting DOEP Exemptions...")
    exemptions_df = spark.read.csv(cfg.RAW_EXEMPTIONS, header=True, inferSchema=True)
    exemptions_df.write.mode("overwrite").parquet(cfg.CANONICAL_EXEMPTIONS)
    
    print("Ingesting Transactions...")
    transactions_df = spark.read.csv(cfg.RAW_TRANSACTIONS, header=True, schema=TRANSACTIONS_SCHEMA)
    transactions_df.write.mode("overwrite").partitionBy("is_cash").parquet(cfg.CANONICAL_TRANSACTIONS)
    
    print("Ingestion complete.")
    spark.stop()

if __name__ == "__main__":
    run_ingestion()
