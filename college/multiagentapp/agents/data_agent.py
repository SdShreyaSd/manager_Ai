import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

class DataAgent:
    def __init__(self):
        self.data = None
        self.preprocessed_data = None
        self.data_info = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def read_data(self, file_path: str) -> bool:
        """
        Read data from CSV or Excel file
        """
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            else:
                self.logger.error("Unsupported file format. Please use CSV or Excel files.")
                return False
            
            self._analyze_data()
            return True
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            return False

    def _analyze_data(self):
        """
        Analyze the loaded data and store information
        """
        if self.data is None:
            return

        self.data_info = {
            'num_rows': len(self.data),
            'num_columns': len(self.data.columns),
            'column_types': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.data.select_dtypes(include=['object']).columns)
        }

    def preprocess_data(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Preprocess the data based on configuration
        """
        if self.data is None:
            self.logger.error("No data loaded. Please load data first.")
            return False

        try:
            # Create a copy of the data for preprocessing
            self.preprocessed_data = self.data.copy()

            if config is None:
                config = self._get_default_preprocessing_config()

            # Handle missing values
            self._handle_missing_values(config.get('missing_values', {}))

            # Encode categorical variables
            self._encode_categorical(config.get('categorical_encoding', {}))

            # Scale numerical variables
            self._scale_numerical(config.get('scaling', {}))

            return True
        except Exception as e:
            self.logger.error(f"Error during preprocessing: {str(e)}")
            return False

    def _get_default_preprocessing_config(self) -> Dict[str, Any]:
        """
        Get default preprocessing configuration
        """
        return {
            'missing_values': {
                'numeric': 'mean',
                'categorical': 'mode'
            },
            'categorical_encoding': {
                'method': 'label'
            },
            'scaling': {
                'method': 'standard'
            }
        }

    def _handle_missing_values(self, config: Dict[str, str]):
        """
        Handle missing values in the dataset
        """
        numeric_cols = self.data_info['numeric_columns']
        categorical_cols = self.data_info['categorical_columns']

        # Handle numeric columns
        for col in numeric_cols:
            if self.preprocessed_data[col].isnull().any():
                if config.get('numeric') == 'mean':
                    self.preprocessed_data[col].fillna(self.preprocessed_data[col].mean(), inplace=True)
                elif config.get('numeric') == 'median':
                    self.preprocessed_data[col].fillna(self.preprocessed_data[col].median(), inplace=True)

        # Handle categorical columns
        for col in categorical_cols:
            if self.preprocessed_data[col].isnull().any():
                if config.get('categorical') == 'mode':
                    self.preprocessed_data[col].fillna(self.preprocessed_data[col].mode()[0], inplace=True)

    def _encode_categorical(self, config: Dict[str, str]):
        """
        Encode categorical variables
        """
        categorical_cols = self.data_info['categorical_columns']
        
        if config.get('method') == 'label':
            for col in categorical_cols:
                self.preprocessed_data[col] = pd.Categorical(self.preprocessed_data[col]).codes
        elif config.get('method') == 'onehot':
            self.preprocessed_data = pd.get_dummies(self.preprocessed_data, columns=categorical_cols)

    def _scale_numerical(self, config: Dict[str, str]):
        """
        Scale numerical variables
        """
        numeric_cols = self.data_info['numeric_columns']
        
        if config.get('method') == 'standard':
            for col in numeric_cols:
                mean = self.preprocessed_data[col].mean()
                std = self.preprocessed_data[col].std()
                self.preprocessed_data[col] = (self.preprocessed_data[col] - mean) / std
        elif config.get('method') == 'minmax':
            for col in numeric_cols:
                min_val = self.preprocessed_data[col].min()
                max_val = self.preprocessed_data[col].max()
                self.preprocessed_data[col] = (self.preprocessed_data[col] - min_val) / (max_val - min_val)

    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded data
        """
        return self.data_info

    def get_preprocessed_data(self):
        """
        Get the preprocessed data
        """
        return self.preprocessed_data

    def get_raw_data(self):
        """
        Get the raw data
        """
        return self.data 