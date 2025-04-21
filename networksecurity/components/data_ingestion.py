from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

#configuration of the data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig

import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split

# Read fron mongo db

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    '''
    1.read from mongodb
    2.store in csv format in feature store
    3.data ingestion
    '''

    # providing dataIngestion config data
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        ''' 
        This fuction will provide all the required directies and details that needed for configuring 
        taken from DataIngestionConfig modul 
        '''
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_collection_as_dataframe(self):
        ''' 
        Read data from mongodb
        convert to df. drop default _id column,
        handle missing values 
        return df
        
        '''
        try:
            data_base_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[data_base_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list:
                df = df.drop(columns=['_id'],axis=1)
            
            #replace missing values

            df.replace({"na":np.nan},inplace=True)

            return df


        except Exception as e:
            raise NetworkSecurityException(e,sys)


    def export_data_into_feature_store(self,dataframe:pd.DataFrame):
        '''
        This fuction will take the dataframe that extracted from mongodb. Create a directory 
        for feature store. Save csv file 
        '''

        try:
            #get the directory of feature store from IngestionConfig
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            #create folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def split_data_as_train_test(self,dataframe:pd.DataFrame):
        try:
            train_set,test_set = train_test_split(
                dataframe,test_size=self.data_ingestion_config.train_test_split_ratio

            )
            logging.info("Preformed train test split on the dataframe")
            logging.info("existing split_data_as_train_test method of Data_Ingestion_class")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)

            logging.info(f"Exporting train and test file path")

            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)

            test_set.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)

            logging.info(f"Exported train and test path.")

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_ingestion(self):
        try:
            dataframe  = self.export_collection_as_dataframe() # step 1 get data from mongodb
            dataframe = self.export_data_into_feature_store(dataframe) # step 2 store in feature store
            self.split_data_as_train_test(dataframe)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
