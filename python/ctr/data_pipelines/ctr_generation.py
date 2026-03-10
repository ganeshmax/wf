from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, to_date, expr, collect_list
import os
import json

from data_pipelines.utils import get_spark_session
import data_pipelines.config as cfg

def run_ctr_generation():
    spark = get_spark_session("CTRGeneration")
        
    print("Reading Canonical Transactions & Account Owners for Secondary Relational Joins...")
    tx_df = spark.read.parquet(cfg.CANONICAL_TRANSACTIONS).filter(col("is_cash") == True)
    owners_df = spark.read.parquet(cfg.CANONICAL_ACCOUNT_OWNERS)
    
    # Map Business Days: Saturday (7) -> Monday, Sunday (1) -> Monday
    tx_df = tx_df.withColumn("raw_date", to_date(col("timestamp")))
    tx_df = tx_df.withColumn(
        "date",
        expr(
            "CASE " +
            "WHEN dayofweek(raw_date) = 7 THEN date_add(raw_date, 2) " +
            "WHEN dayofweek(raw_date) = 1 THEN date_add(raw_date, 1) " +
            "ELSE raw_date END"
        )
    )
    
    # JOINT ACCOUNT EXPLOSION JOIN
    tx_with_owners_df = tx_df.join(owners_df, "account_id", "inner") \
                             .withColumnRenamed("customer_id", "beneficiary_id")
    
    tx_in = tx_with_owners_df.filter(col("transaction_type") == "DEPOSIT")
    tx_out = tx_with_owners_df.filter(col("transaction_type") == "WITHDRAWAL")
        
    print("Reading 4 distinct Aggregated Daily Totals...")
    ben_in = spark.read.parquet(cfg.AGG_BEN_IN)
    ben_out = spark.read.parquet(cfg.AGG_BEN_OUT)
    cond_in = spark.read.parquet(cfg.AGG_COND_IN)
    cond_out = spark.read.parquet(cfg.AGG_COND_OUT)
    
    # 1. Identify Triggers (>10k)
    trigger_ben_in = ben_in.filter(col("total_amount") > cfg.CTR_THRESHOLD)
    trigger_ben_out = ben_out.filter(col("total_amount") > cfg.CTR_THRESHOLD)
    trigger_cond_in = cond_in.filter(col("total_amount") > cfg.CTR_THRESHOLD)
    trigger_cond_out = cond_out.filter(col("total_amount") > cfg.CTR_THRESHOLD)
    
    # 2. Extract Primaries and Resolving Secondaries via Joins
    # We assign a unique UUID to every single discrete triggering event to group all resulting Forms.
    
    trigger_ben_in = trigger_ben_in.withColumn("report_id", expr("uuid()"))
    primary_ben_in = tx_in.join(trigger_ben_in, ["beneficiary_id", "date"]) \
        .groupBy("report_id", "beneficiary_id", "date", "total_amount") \
        .agg(collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("beneficiary_id").alias("customer_id"), "date", lit("Primary Beneficiary").alias("ctr_role"), lit("Cash-In").alias("direction"), col("total_amount").alias("report_amount"), col("total_amount").alias("entity_amount"), col("transaction_ids"))
    sec_cond_in = tx_in.join(trigger_ben_in, ["beneficiary_id", "date"]) \
        .groupBy("report_id", "conductor_id", "date", "total_amount") \
        .agg(expr("sum(amount)").alias("entity_amount"), collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("conductor_id").alias("customer_id"), "date", lit("Secondary Conductor").alias("ctr_role"), lit("Cash-In").alias("direction"), col("total_amount").alias("report_amount"), col("entity_amount"), col("transaction_ids"))
        
    trigger_ben_out = trigger_ben_out.withColumn("report_id", expr("uuid()"))
    primary_ben_out = tx_out.join(trigger_ben_out, ["beneficiary_id", "date"]) \
        .groupBy("report_id", "beneficiary_id", "date", "total_amount") \
        .agg(collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("beneficiary_id").alias("customer_id"), "date", lit("Primary Beneficiary").alias("ctr_role"), lit("Cash-Out").alias("direction"), col("total_amount").alias("report_amount"), col("total_amount").alias("entity_amount"), col("transaction_ids"))
    sec_cond_out = tx_out.join(trigger_ben_out, ["beneficiary_id", "date"]) \
        .groupBy("report_id", "conductor_id", "date", "total_amount") \
        .agg(expr("sum(amount)").alias("entity_amount"), collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("conductor_id").alias("customer_id"), "date", lit("Secondary Conductor").alias("ctr_role"), lit("Cash-Out").alias("direction"), col("total_amount").alias("report_amount"), col("entity_amount"), col("transaction_ids"))
        
    trigger_cond_in = trigger_cond_in.withColumn("report_id", expr("uuid()"))
    primary_cond_in = tx_in.join(trigger_cond_in, ["conductor_id", "date"]) \
        .groupBy("report_id", "conductor_id", "date", "total_amount") \
        .agg(collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("conductor_id").alias("customer_id"), "date", lit("Primary Conductor").alias("ctr_role"), lit("Cash-In").alias("direction"), col("total_amount").alias("report_amount"), col("total_amount").alias("entity_amount"), col("transaction_ids"))
    sec_ben_in = tx_in.join(trigger_cond_in, ["conductor_id", "date"]) \
        .groupBy("report_id", "beneficiary_id", "date", "total_amount") \
        .agg(expr("sum(amount)").alias("entity_amount"), collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("beneficiary_id").alias("customer_id"), "date", lit("Secondary Beneficiary").alias("ctr_role"), lit("Cash-In").alias("direction"), col("total_amount").alias("report_amount"), col("entity_amount"), col("transaction_ids"))
        
    trigger_cond_out = trigger_cond_out.withColumn("report_id", expr("uuid()"))
    primary_cond_out = tx_out.join(trigger_cond_out, ["conductor_id", "date"]) \
        .groupBy("report_id", "conductor_id", "date", "total_amount") \
        .agg(collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("conductor_id").alias("customer_id"), "date", lit("Primary Conductor").alias("ctr_role"), lit("Cash-Out").alias("direction"), col("total_amount").alias("report_amount"), col("total_amount").alias("entity_amount"), col("transaction_ids"))
    sec_ben_out = tx_out.join(trigger_cond_out, ["conductor_id", "date"]) \
        .groupBy("report_id", "beneficiary_id", "date", "total_amount") \
        .agg(expr("sum(amount)").alias("entity_amount"), collect_list("transaction_id").alias("transaction_ids")) \
        .select(col("report_id"), col("beneficiary_id").alias("customer_id"), "date", lit("Secondary Beneficiary").alias("ctr_role"), lit("Cash-Out").alias("direction"), col("total_amount").alias("report_amount"), col("entity_amount"), col("transaction_ids"))

    # 3. Union all reportable entities
    ctr_candidates_df = primary_ben_in \
        .unionByName(sec_cond_in) \
        .unionByName(primary_ben_out) \
        .unionByName(sec_cond_out) \
        .unionByName(primary_cond_in) \
        .unionByName(sec_ben_in) \
        .unionByName(primary_cond_out) \
        .unionByName(sec_ben_out)
    
    # Drop exact duplicates within the SAME report (e.g. if a Conductor made 3 sub-deposits for a single Beneficiary, we only list them once on that Beneficiary's form)
    # But a person CAN be legally listed on multiple different report_ids.
    ctr_candidates_df = ctr_candidates_df.dropDuplicates(["report_id", "customer_id", "date", "ctr_role", "direction"])
    
    print("Applying DOEP Exemptions...")
    exemptions_df = spark.read.parquet(cfg.CANONICAL_EXEMPTIONS)
    ctr_candidates_df = ctr_candidates_df.join(exemptions_df, on="customer_id", how="left_anti")
    
    print("Enriching with Customer Metadata...")
    customers_df = spark.read.parquet(cfg.CANONICAL_CUSTOMERS)
    non_customers_df = spark.read.parquet(cfg.CANONICAL_NON_CUSTOMERS)
    
    # Create a universal lookup table bridging true accounts and non-customer shadows
    universal_entities_df = customers_df.unionByName(non_customers_df, allowMissingColumns=True)
    
    # Join to get PII for the CTR report
    ctr_df = ctr_candidates_df.join(universal_entities_df, on="customer_id", how="inner")
    
    # 4. Phase 10: Maker / Checker Validation Rules
    print("Executing Maker/Checker Validation...")
    ctr_df = ctr_df.withColumn(
        "status", 
        expr("CASE WHEN tin IS NULL OR address IS NULL THEN 'ACTION_REQUIRED' ELSE 'PENDING_REVIEW' END")
    )
    
    print("Writing CTR Data...")
    ctr_df = ctr_df.orderBy("customer_id", "ctr_role")
    ctr_df.write.mode("overwrite").parquet(cfg.CTR_REPORTS)
    
    # Calculate Statistics
    total_customers_processed = universal_entities_df.count()
    total_forms = ctr_candidates_df.select("report_id").distinct().count()
    total_customers_with_ctrs = ctr_candidates_df.select("customer_id").distinct().count()
    
    # Detailed stats
    cash_in_ctrs = ctr_candidates_df.filter(col("direction") == "Cash-In").select("customer_id").distinct().count()
    cash_out_ctrs = ctr_candidates_df.filter(col("direction") == "Cash-Out").select("customer_id").distinct().count()
    
    total_customers_without_ctrs = total_customers_processed - total_customers_with_ctrs
    
    stats = {
        "total_processed": total_customers_processed,
        "total_forms": total_forms,
        "total_with_ctrs": total_customers_with_ctrs,
        "total_without_ctrs": total_customers_without_ctrs,
        "cash_in_ctrs": cash_in_ctrs,
        "cash_out_ctrs": cash_out_ctrs
    }
    
    os.makedirs(cfg.CTR_DIR, exist_ok=True)
    with open(cfg.CTR_STATS, "w") as f:
        json.dump(stats, f)
        
    print("CTR Generation complete. Stats generated.")
    spark.stop()

if __name__ == "__main__":
    run_ctr_generation()
