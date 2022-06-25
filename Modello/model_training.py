import shutil
import pyspark.sql.functions as funcs

from pyspark import SparkFiles
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LinearSVC
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline


APP_NAME = 'clash_attack_pred_model_training'
APP_DATASET_PATH = './data/dataset_Log2.csv'
APP_DATASET_FILE = 'dataset_Log2.csv'

#--------------------------------------------------------#
#|
#|  Descrizione delle features.
#|
#--------------------------------------------------------#

REQUIRED_FEATURES = [
    'Crown',    
    'KingTower',      
    'LeftPrincess',   
    'RigthPrincess',     
    'CrownOpponent',      
    'KingTowerOpponent',  
    'LeftPrincessOpponent',    
    'RigthPrincessOpponent',  
]


def clear():
    shutil.rmtree('./model', ignore_errors=True)

def main():

    #--------------------------------------------------------#
    #|
    #|  Inizializzazione SparkSession e caricamento dataset
    #|
    #--------------------------------------------------------#
    print("-------------------------------------------------")

    spark = SparkSession.builder.appName(APP_NAME) \
        .config("spark.files.overwrite", "true") \
        .getOrCreate()

    spark.sparkContext.addFile(APP_DATASET_PATH)
    dataset_path = SparkFiles.get(APP_DATASET_FILE)

    df = spark.read.format('csv') \
            .option('header', True) \
            .load(dataset_path)

    """print("Show di df")
    df.show()"""

    #--------------------------------------------------------#
    #|
    #|  Feature selection e casting a float.
    #|
    #--------------------------------------------------------#

  
    dataset = df.select(
        funcs.col('Crown').cast('float'),
        funcs.col('KingTower').cast('float'),
        funcs.col('LeftPrincess').cast('float'),
        funcs.col('RigthPrincess').cast('float'),
        funcs.col('CrownOpponent').cast('float'),
        funcs.col('KingTowerOpponent').cast('float'),
        funcs.col('LeftPrincessOpponent').cast('float'),
        funcs.col('RigthPrincessOpponent').cast('float'),
        funcs.col('Cluster').cast('float'),
    )

    """print("Show dataset")
    dataset.show()"""

    #--------------------------------------------------------#
    #|
    #|  Creazione della pipeline.
    #|
    #--------------------------------------------------------#


    asb = VectorAssembler(inputCols=REQUIRED_FEATURES, outputCol='features')
    scl = StandardScaler(inputCol='features', outputCol='scaled_features', withMean=True, withStd=True)
    svm = LinearSVC(labelCol='Cluster', featuresCol='scaled_features', maxIter=100, regParam=.1)
    pipeline = Pipeline(stages=[asb, scl, svm])


    #--------------------------------------------------------#
    #|
    #|  Training ed Evaluation
    #|
    #--------------------------------------------------------#

    (training_data, test_data) = dataset.randomSplit([ .8, .2 ])


    """print("Show training_data")
    training_data.show()

    print("Show test_data")
    test_data.show()"""


    pipeline_model = pipeline.fit(training_data)
    predictions = pipeline_model.transform(test_data)

    evaluator = MulticlassClassificationEvaluator(
        labelCol='Cluster', 
        predictionCol='prediction', 
        metricName='accuracy'
    )

    accuracy = evaluator.evaluate(predictions)
    print('Test accuracy = ', accuracy)

    #--------------------------------------------------------#
    #|
    #|  Salvataggio della pipeline
    #|
    #--------------------------------------------------------#

    pipeline_model.save('model')



if __name__ == '__main__':
    clear()
    main()

"""
Per far funzionare la creazione del modello bisogna impostare correttamente le JAVA_HOME, nel mio caso è stata impostata in questo modo
export JAVA_HOME="/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/"
export PATH=$PATH:$JAVA_HOME/bin
"""
