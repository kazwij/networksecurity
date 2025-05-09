from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp # this is to check data drift 
import pandas as pd
import os,sys
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

class DataValidation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig
                 ):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path) 
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    

    def validate_number_of_columns(self, dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self.schema_config)
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns : {len(dataframe.columns)}")

            if len(dataframe.columns ) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def check_for_numerical_column(self,dataframe:pd.DataFrame)->bool:
        try:
            has_numerical_columns = not dataframe.select_dtypes(include='number').empty
            logging.info(f"Has numerical columns: {has_numerical_columns}")

            return has_numerical_columns
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def detect_dataset_drift(self,base_df,current_df,threshold =0.05)->bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1,d2)

                if threshold <= is_same_dist.pvalue:
                    is_found = True
                else:
                    is_found=False
                    status = False
                report.update({column:{
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status" : is_found
                    }})
            #get drift report 
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            #making dir
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
         

    def initial_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            ## read the data from the train and test 
            train_dataframe  = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)
            
            ## validate number of columns 
            status =self.validate_number_of_columns(train_dataframe)
            if not status:
                erorr_message =f"Train dataframe does not contain all columns.\n"
            
            
            status =self.validate_number_of_columns(test_dataframe)
            if not status:
                erorr_message=f"Test dataframe does not contain all colunmns. \n"

            status = self.check_for_numerical_column(train_dataframe)
            if not status:
               erorr_message=f"Train dataframe does not contain numerical columns. \n" 

            status = self.check_for_numerical_column(test_dataframe)
            if not status:
               erorr_message=f"Test dataframe does not contain numerical columns. \n"

            ## check data drift 
            status = self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,index=False,header=False
            )

            test_dataframe.to_csv(

                self.data_validation_config.valid_test_file_path,index=False,header=False
            )

            data_validation_artifact = DataValidationArtifact(

                validation_status = status,
                valid_train_file_path = self.data_ingestion_artifact.train_file_path,
                valid_test_file_path = self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path = None,
                invalid_test_file_path = None,
                drift_report_file_path = self.data_validation_config.drift_report_file_path

            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
       