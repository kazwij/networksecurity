import os
import sys
import json 

# get url from .env 
from dotenv import load_dotenv 
load_dotenv() #initialize 

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
#print(MONGO_DB_URL) # checking 

#to certify secure connection. 
import certifi
ca=certifi.where()


# loading csv data  
import pandas as pd
import numpy as np
import pymongo
from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():

    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def cvs_to_json_converter(self,file_path):
        '''
        This fuction will take a csv file and convert it into json format
        '''
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)#drop index
            records = list(json.loads(data.T.to_json()).values())#convert to json and convert to list type
            
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.records=records
            self.database=database
            self.collection=collection

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]

            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)

            return(len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e,sys)

if __name__=='__main__':
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE="Kasun"
    Collection="NetworkData"
    networkbj=NetworkDataExtract()
    records = networkbj.cvs_to_json_converter(file_path=FILE_PATH)
    print(records)
    no_of_records = networkbj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)

