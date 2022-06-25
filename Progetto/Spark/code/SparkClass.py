from ast import Str
from functools import partial
import pandas as pd
import json
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import *
from pyspark.sql.types import StructType,StructField, StringType
from elasticsearch import Elasticsearch
from datetime import datetime
from time import sleep
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
from pyspark.sql import types as st

from pyspark.ml import PipelineModel



APP_NAME = 'clashRoyale-streaming-prediction'
APP_BATCH_INTERVAL = 1

elastic_host="http://elasticsearch:9200"
elastic_index="royale_es"
kafkaServer="kafkaserver:9092"
topic = "clahsroyale"

es = Elasticsearch(
    elastic_host,
    verify_certs=False
    )

def process_batch(batch_df, batch_id):
    for idx, row in enumerate(batch_df.collect()):
        row_dict = row.asDict()
        id = f'{batch_id}-{idx}'
        resp = es.index(index=elastic_index, id=id, document=row_dict)
        print(resp)
    batch_df.show()


###        AGGIUNTE

def get_record_schema():
    return tp.StructType([
        tp.StructField('timestamp',                tp.StringType()),
        tp.StructField('Crown',                    tp.IntegerType()),
        tp.StructField('KingTower',                tp.IntegerType()),
        tp.StructField('LeftPrincess',             tp.IntegerType()),
        tp.StructField('RigthPrincess',            tp.IntegerType()),
        tp.StructField('CrownOpponent',            tp.IntegerType()),
        tp.StructField('KingTowerOpponent',        tp.IntegerType()),
        tp.StructField('LeftPrincessOpponent',     tp.IntegerType()),
        tp.StructField('RigthPrincessOpponent',    tp.IntegerType()),
    ])


#NO
spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

model = PipelineModel.load("model")
schema = get_record_schema()


# Define Training Set Structure
#Camabaire tutto un String
clashKafka = tp.StructType([
    tp.StructField(name= 'timestamp', dataType= tp.StringType()),
    tp.StructField(name= 'Crown', dataType= tp.IntegerType()),
    tp.StructField(name= 'KingTower', dataType= tp.IntegerType()),
    tp.StructField(name= 'LeftPrincess', dataType= tp.IntegerType()),
    tp.StructField(name= 'RigthPrincess', dataType= tp.IntegerType()),
    tp.StructField(name= 'CrownOpponent', dataType= tp.IntegerType()),
    tp.StructField(name= 'KingTowerOpponent', dataType= tp.IntegerType()),
    tp.StructField(name= 'LeftPrincessOpponent', dataType= tp.IntegerType()),
    tp.StructField(name= 'RigthPrincessOpponent', dataType= tp.IntegerType()),
])




# Streaming Query
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()




df = df.selectExpr("CAST(timestamp AS STRING)","CAST(value AS STRING)")\
        .select(from_json("value", clashKafka).alias("data"))\
        .select("data.*")


results = model.transform(df)



results = results.drop("features", "scaled_features","rawPrediction")


results = results.writeStream \
    .foreachBatch(process_batch) \
    .start()

results.awaitTermination()
