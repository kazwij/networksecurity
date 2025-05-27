from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation

from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig

from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import ModelTrainerConfig 
import sys

if __name__ =='__main__':
     try:
          trainingpipelineconfig = TrainingPipelineConfig()
          dataingestionconfig =  DataIngestionConfig(trainingpipelineconfig)
          data_ingestion = DataIngestion(dataingestionconfig)
          logging.info("Initiate the data ingestion")
          dataingestionartifact = data_ingestion.initiate_data_ingestion()
          logging.info("Data Initiation complete")
          print(dataingestionartifact)
          datavalidationconfig = DataValidationConfig(trainingpipelineconfig)
          data_validation = DataValidation(dataingestionartifact,datavalidationconfig)
          logging.info("Initiate the Data Validation")
          data_validation_artifact = data_validation.initial_data_validation()
          logging.info("data validation completed")
          print(data_validation_artifact)
          data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
          logging.info("Data transformation start")
          data_transformation = DataTransformation(data_validation_artifact,data_transformation_config)
          data_transformation_artifact = data_transformation.initiate_data_transformation()
          print(data_transformation_artifact)
          logging.info("Data transformation completed")
          
          logging.info("Model Training started")
          model_training_config = ModelTrainerConfig(trainingpipelineconfig)
          logging.info("model trainign config done")
          model_trainer = ModelTrainer(model_trainer_config=model_training_config,data_transformation_artifact=data_transformation_artifact)
          model_trainer_artifact = model_trainer.initiate_model_trainer()
          
          logging.info("Model Training artifact created")
           

     except Exception as e:
          raise NetworkSecurityException(e,sys)