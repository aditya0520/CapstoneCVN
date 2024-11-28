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

    def create_new_sheet(self, sheet_name, df):
        """
        Creates a new sheet with column definitions based on a DataFrame.

        Parameters:
        sheet_name (str): The name of the new sheet to be created.
        df (pd.DataFrame): The DataFrame containing the column headers.

        Returns:
        dict: The API response containing details of the created sheet.
        """
        # Define columns based on DataFrame headers
        columns = [{'title': col, 'primary': i == 0, 'type': 'TEXT_NUMBER'} for i, col in enumerate(df.columns)]
        
        # Construct the payload
        payload = {
            'name': sheet_name,
            'columns': columns
        }
        
        # API endpoint to create a sheet
        url = 'https://api.smartsheet.com/2.0/sheets'
        response = requests.post(url, json=payload, headers=self.headers)
        
        # Return the response (sheet details)
        return response.json()

    def add_rows_to_sheet(self, sheet_id, df):
        """
        Adds rows to an existing Smartsheet based on a DataFrame.

        Parameters:
        sheet_id (str): The ID of the Smartsheet.
        df (pd.DataFrame): The DataFrame containing the data to add as rows.

        Returns:
        dict: The API response indicating success or failure.
        """
        # Fetch the column IDs for the sheet
        url = f'https://api.smartsheet.com/2.0/sheets/{sheet_id}'
        response = requests.get(url, headers=self.headers)
        sheet_data = response.json()
        column_map = {col['title']: col['id'] for col in sheet_data['columns']}
        
        # Convert DataFrame rows to Smartsheet row format
        rows_to_add = []
        for _, row in df.iterrows():
            cells = [{'columnId': column_map[col], 'value': row[col]} for col in df.columns if col in column_map]
            rows_to_add.append({'cells': cells})
        
        # Send the rows to Smartsheet
        add_rows_url = f'https://api.smartsheet.com/2.0/sheets/{sheet_id}/rows'
        payload = rows_to_add
        response = requests.post(add_rows_url, json=payload, headers=self.headers)
        
        return response.json()