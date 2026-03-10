from pyspark.sql import SparkSession

def get_spark_session(app_name: str) -> SparkSession:
    """
    Returns a configured SparkSession.
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
