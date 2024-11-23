import requests
import pandas as pd

class SmartsheetFetcher:
    """
    A class to interact with the Smartsheet API and fetch sheet data as Pandas DataFrames.
    """

    def __init__(self, bearer_token):
        """
        Initializes the SmartsheetFetcher with the required API bearer token.

        Parameters:
        bearer_token (str): The Smartsheet API bearer token for authorization.
        """
        self.bearer_token = bearer_token
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

    def fetch_all_sheets(self):
        """
        Fetches all available sheets and returns their data in a dictionary of DataFrames.

        Returns:
        dict: A dictionary where each key is the sheet name, and each value is a DataFrame containing the sheet's data.
        """
        url = 'https://api.smartsheet.com/2.0/sheets'
        response = requests.get(url, headers=self.headers)
        sheets_data = response.json().get('data', [])
        
        all_sheets_data = {}
        
        for sheet_info in sheets_data:
            sheet_id = sheet_info['id']
            sheet_name = sheet_info['name']
            all_sheets_data[sheet_name] = sheet_id
        
        return all_sheets_data

    def fetch_smartsheet_data(self, sheet_id):
        """
        Fetches Smartsheet data and returns it as a Pandas DataFrame.

        Parameters:
        sheet_id (str): The ID of the Smartsheet to fetch data from.

        Returns:
        pd.DataFrame: DataFrame containing the sheet's data.
        """
        url = f'https://api.smartsheet.com/2.0/sheets/{sheet_id}'
        
        response = requests.get(url, headers=self.headers)
        sheet_data = response.json()
        
        columns = {col['id']: col['title'] for col in sheet_data['columns']}
        data = []
        
        for row in sheet_data['rows']:
            row_data = {columns[cell['columnId']]: cell.get('value', None) for cell in row['cells']}
            data.append(row_data)
        
        df = pd.DataFrame(data)
        df = df.dropna(how='all')
        
        return df
