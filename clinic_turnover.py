import pandas as pd
import numpy as np
import re  
import openpyxl 


class ClinicTurnover:
    """
    A class to process clinic turnover data for a specified grant year period. It merges data from two consecutive years,
    formats it, and calculates summary statistics. It also generates an Excel file with the processed data.

    Attributes:
    - df_prev_year (pd.DataFrame): The previous year's data.
    - df_curr_year (pd.DataFrame): The current year's data.
    - clinic_code (str): The clinic code for naming the output file.
    - grant_start_date (str): The start date of the grant year period.
    - grant_end_date (str): The end date of the grant year period.
    """
    
    def __init__(self, df_prev_year, df_curr_year, clinic_code, grant_start_date, grant_end_date):
        """
        Initializes the ClinicDataProcessor with the required data and parameters.

        Parameters:
        - df_prev_year (pd.DataFrame): DataFrame for the previous year's data.
        - df_curr_year (pd.DataFrame): DataFrame for the current year's data.
        - clinic_code (str): The code for the clinic.
        - grant_start_date (str): The start date of the grant year period in 'YYYY-MM-DD' format.
        - grant_end_date (str): The end date of the grant year period in 'YYYY-MM-DD' format.
        """
        # Validate DataFrames
        if not isinstance(df_prev_year, pd.DataFrame):
            raise TypeError("df_prev_year must be a pandas DataFrame")
        if not isinstance(df_curr_year, pd.DataFrame):
            raise TypeError("df_curr_year must be a pandas DataFrame")

        # Validate clinic_code
        if not isinstance(clinic_code, str):
            raise TypeError("clinic_code must be a string")

        # Validate date formats
        try:
            pd.to_datetime(grant_start_date)
        except ValueError:
            raise ValueError("grant_start_date must be a valid date in 'YYYY-MM-DD' format")
        try:
            pd.to_datetime(grant_end_date)
        except ValueError:
            raise ValueError("grant_end_date must be a valid date in 'YYYY-MM-DD' format")

        self.df_prev_year = df_prev_year
        self.df_curr_year = df_curr_year
        self.clinic_code = clinic_code
        self.grant_start_date = grant_start_date
        self.grant_end_date = grant_end_date

    def process_data(self):
        """
        Processes the clinic turnover data and prepares it for export to Excel.

        Returns:
        - pd.DataFrame: The processed DataFrame containing merged and formatted data with summaries.
        """

        # Check if required columns exist
        required_columns = ['Month Start', 'Month End', 'Turnover']
        for col in required_columns:
            if col not in self.df_prev_year.columns:
                raise KeyError(f"Column '{col}' not found in df_prev_year")
            if col not in self.df_curr_year.columns:
                raise KeyError(f"Column '{col}' not found in df_curr_year")

        # Convert date columns to datetime
        try:
            self.df_prev_year['Month Start'] = pd.to_datetime(self.df_prev_year['Month Start'])
            self.df_prev_year['Month End'] = pd.to_datetime(self.df_prev_year['Month End'])
            self.df_curr_year['Month Start'] = pd.to_datetime(self.df_curr_year['Month Start'])
            self.df_curr_year['Month End'] = pd.to_datetime(self.df_curr_year['Month End'])
        except Exception as e:
            raise ValueError(f"Error converting 'Month Start' or 'Month End' to datetime: {e}")

        # Filter data according to the grant year period
        data_prev_year_filtered = self.df_prev_year[self.df_prev_year['Month Start'] >= pd.to_datetime(self.grant_start_date)]
        data_curr_year_filtered = self.df_curr_year[self.df_curr_year['Month End'] <= pd.to_datetime(self.grant_end_date)]

        # Concatenate the filtered data
        grant_year_data = pd.concat([data_prev_year_filtered, data_curr_year_filtered], ignore_index=True)

        # Check if 'Turnover' column is numeric
        if not pd.api.types.is_numeric_dtype(grant_year_data['Turnover']):
            raise TypeError("'Turnover' column must be numeric")

        grant_year_data['Month Start'] = pd.to_datetime(grant_year_data['Month Start'])
        grant_year_data['Month End'] = pd.to_datetime(grant_year_data['Month End'])

        # Formatting dates and percentages
        grant_year_data['Month Start'] = grant_year_data['Month Start'].dt.strftime('%m/%d/%y')
        grant_year_data['Month End'] = grant_year_data['Month End'].dt.strftime('%m/%d/%y')
        grant_year_data['Turnover'] = grant_year_data['Turnover'].map("{:.0%}".format)

        # Check for null values in 'Month Start' after formatting
        if grant_year_data['Month Start'].isnull().any():
            raise ValueError("'Month Start' contains null values after formatting")

        # Insert year rows based on changes in the year
        final_data = grant_year_data.copy()
        years = final_data['Month Start'].apply(lambda x: x[-2:]).drop_duplicates().tolist()
        year_rows = []

        # Compute positions to insert year rows
        for year in years:
            year_position = final_data[final_data['Month Start'].str.endswith(year)].index.min()
            year_rows.append((year_position, {'Primary Column': f"20{year}", 'Month #': np.nan, 
                                              '# Separated Employees': np.nan, 'Avg # Employees': np.nan, 
                                              'Turnover': '', 'Month Start': '', 'Month End': ''}))

        # Insert year rows into the DataFrame
        for index, year_row in reversed(year_rows):
            final_data = pd.concat([final_data.iloc[:index], pd.DataFrame([year_row]), final_data.iloc[index:]]).reset_index(drop=True)

        # Append a row for the totals
        total_row_index = len(final_data) + 2  # Adjust for header and one-based index
        summary_df = pd.DataFrame([{
            'Primary Column': 'Total', 
            'Month #': '', 
            '# Separated Employees': f"=SUM(C2:C{total_row_index-1})", 
            'Avg # Employees': f"=AVERAGE(D2:D{total_row_index-1})", 
            'Turnover': f"=TEXT(C{total_row_index}/D{total_row_index}, \"0%\")",  # Formula to calculate and format as percentage
            'Month Start': '', 
            'Month End': ''
        }])
        final_data = pd.concat([final_data, summary_df], ignore_index=True)

        return final_data