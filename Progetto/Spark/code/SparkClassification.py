from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark import SparkContext
from pyspark.sql import SparkSession
from elasticsearch import Elasticsearch
from pyspark.sql.functions import col

elastic_host="http://elasticsearch:9200"
elastic_index="taptweet"
kafkaServer="kafkaserver:9092"
topic = "clahsroyale"


## is there a field in the mapping that should be used to specify the ES document ID
# "es.mapping.id": "id"
# Credit for mapping https://medium.com/@CMpoi/elasticsearch-defining-the-mapping-of-twitter-data-dafad0f50695 Timestamp

# es_mapping = {
#     "mappings": {
#         "properties": 
#             {
#                 "created_at": {"type": "text","format": "EEE MMM dd HH:mm:ss Z yyyy"},
#                 "text": {"type": "text","fielddata": True}
#             }
#     }
# }
#es = Elasticsearch(hosts=elastic_host) 
# make an API call to the Elasticsearch cluster
# and have it return a response:
# response = es.indices.create(
#     index=elastic_index,
#     body=es_mapping,
#     ignore=400 # ignore 400 already exists code
# )

# if 'acknowledged' in response:
#     if response['acknowledged'] == True:
#         print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])


def process_batch(batch_df, batch_id):
   batch_df.show()


# Define Training Set Structure
tweetKafka = tp.StructType([
    tp.StructField(name= 'TagPplayer', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'BattleTime', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'Crown', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'KingTower', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'LeftPrincess', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'RigthPrincess', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'CrownOpponent', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'KingTowerOpponent', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'LeftPrincessOpponent', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'RigthPrincessOpponent', dataType= tp.IntegerType(),  nullable= True),
])

pseudoSchema = tp.StructType([
    tp.StructField(name="message", dataType=tp.StringType())
])

# sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
#                         .set("es.port", "9200")

sc = SparkContext(appName="TapSentiment")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

# Streaming Query

# Read the stream from kafka
# df = spark \
#     .readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", kafkaServer) \
#     .option("subscribe", topic) \
#     .load()

df = spark.readStream.format('kafka') \
    .option('kafka.bootstrap.servers', kafkaServer) \
    .option('subscribe', topic) \
    .load() \
    .select(from_json(col("value").cast("string"), pseudoSchema).alias("data")) \
    .select(from_json(col("message"), tweetKafka).alias("data")) \
    .selectExpr("message.*")

# Cast the message received from kafka with the provided schema
# df = df.selectExpr("CAST(value AS STRING)") \
#     .select(from_json("value", tweetKafka).alias("data")) \
#     .select("data.*")

df.writeStream \
    .format("console") \
    .outputMode("append") \
    .start() \
    .awaitTermination()

# df.writeStream \
#         .foreachBatch(process_batch) \
#         .start() \
#         .awaitTermination()





# df.start().awaitTermination()

# print(df)

# Write the stream to elasticsearch
# df.writeStream \
#     .option("checkpointLocation", "/save/location") \
#     .format("es") \
#     .start(elastic_index) \
#     .awaitTermination()

