import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import datetime


class MonthsWorked:
    def __init__(self, input_df, report_start_date, report_end_date):
        """
        Initialize the calculator with input DataFrame and reporting period.
        
        :param input_df: Pandas DataFrame containing the input data
        :param report_start_date: Start date of the reporting period (datetime object)
        :param report_end_date: End date of the reporting period (datetime object)
        """
        self.input_df = input_df
        self.report_start_date = datetime.strptime(report_start_date, '%Y-%m-%d') if isinstance(report_start_date, str) else report_start_date
        self.report_end_date = datetime.strptime(report_end_date, '%Y-%m-%d') if isinstance(report_end_date, str) else report_end_date
        self.df = self.input_df.copy()

    def validate_input_dataframe(self, df):
        """
        Validate the input DataFrame for required columns, datatypes, and values.

        Args:
        - df (pd.DataFrame): The input DataFrame to validate.

        Raises:
        - ValueError: If required columns are missing or datatypes/values are invalid.
        """
        # Check for missing columns
        required_columns = ['Position', 'FTE-Adjusted Months Worked', 'End Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)} in the input data.")

        # Check for empty dataset
        if df.empty:
            raise ValueError("The input DataFrame is empty. Please provide valid data.")

        # Validate datatypes
        if not pd.api.types.is_numeric_dtype(df['FTE-Adjusted Months Worked']):
            raise ValueError("'FTE-Adjusted Months Worked' must be a numeric column.")

        if not pd.api.types.is_string_dtype(df['Position']):
            raise ValueError("'Position' must be a string column.")

        if not (pd.api.types.is_datetime64_any_dtype(df['End Date']) or not pd.api.types.is_string_dtype(df['End Date'])):
            raise ValueError("'End Date' must be a datetime or string column.")

        # Check for negative or missing values in key columns
        if (df['FTE-Adjusted Months Worked'] < 0).any():
            raise ValueError("'FTE-Adjusted Months Worked' contains negative values.")

        if df['Position'].isnull().any():
            raise ValueError("The 'Position' column contains missing values.")

        # Check for duplicates
        if df.duplicated().any():
            raise ValueError("The input DataFrame contains duplicate rows.")
        
    def calculate_months_in_period(self, start_date, end_date, fte, role, name, leave_start=None, leave_end=None, include_start_month=False, skip_first_partial_month=False):
        """
        Calculate months worked within a reporting period.
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if isinstance(leave_start, str):
            leave_start = datetime.strptime(leave_start, '%Y-%m-%d')
        if isinstance(leave_end, str):
            leave_end = datetime.strptime(leave_end, '%Y-%m-%d')

        if start_date < self.report_start_date:
            start_date = self.report_start_date.replace(day=1)
        elif not include_start_month:
            if start_date.day < 16:
                start_date = start_date.replace(day=1)
            else:
                start_date = start_date.replace(day=1) + relativedelta(months=1)

        if skip_first_partial_month and start_date.day > 15:
            start_date = start_date.replace(day=1) + relativedelta(months=2)

        if pd.isna(end_date):
            if pd.notna(leave_start) and pd.isna(leave_end):
                end_date = leave_start - relativedelta(days=1)
            else:
                end_date = self.report_end_date - relativedelta(days=1)
        elif end_date >= self.report_end_date:
            end_date = self.report_end_date - relativedelta(days=1)
        else:
            if end_date.day >= 15:
                end_date = end_date.replace(day=1) - relativedelta(days=1)
            else:
                end_date = end_date.replace(day=1) - relativedelta(months=1) - relativedelta(days=1)

        if start_date > end_date:
            return 0, 0, []

        if pd.notna(leave_start) and pd.notna(leave_end):
            if leave_end < self.report_start_date or leave_start > self.report_end_date:
                leave_start, leave_end = None, None
            else:
                leave_start = max(leave_start, self.report_start_date)
                leave_end = min(leave_end, self.report_end_date)

        months_list = []
        current_date = start_date
        while current_date <= end_date:
            months_list.append(current_date.strftime("%Y-%m"))
            current_date += relativedelta(months=1)

        total_months = len(months_list)

        if pd.notna(leave_start) and pd.notna(leave_end):
            leave_days = (leave_end - leave_start).days
            leave_months = leave_days // 22
            total_months -= leave_months

        total_months = max(0, total_months)
        fte_adjusted_months = total_months * fte

        return total_months, fte_adjusted_months, months_list

    def get_results(self):
        """
        Process the input DataFrame and return the resulting DataFrame with calculated months worked and FTE-adjusted months.
        
        :return: DataFrame with the results
        """
        months_worked_list = []
        fte_adjusted_months_list = []
        months_printed_list = []

        multiple_entry_names = self.df[self.df.duplicated(['Name'], keep=False)]['Name'].unique()

        for _, row in self.df.iterrows():
            start_date = row['Start Date']
            end_date = row['End Date'] if pd.notna(row['End Date']) else None
            fte = row['FTE'] if pd.notna(row['FTE']) else 1
            role = row['Position']
            name = row['Name']
            leave_start = row['Employee Leave (start date)']
            leave_end = row['Employee Leave (end date)']

            multiple_entries = name in multiple_entry_names
            include_start_month = False
            skip_first_partial_month = False

            if multiple_entries:
                months_worked, fte_adjusted_months, months_list = self.calculate_months_in_period(
                    start_date, end_date, fte, role, name, leave_start, leave_end, include_start_month, skip_first_partial_month
                )
            else:
                months_worked, fte_adjusted_months, months_list = self.calculate_months_in_period(
                    start_date, end_date, fte, role, name, leave_start, leave_end, include_start_month, skip_first_partial_month
                )

            months_worked_list.append(months_worked)
            fte_adjusted_months_list.append(fte_adjusted_months)
            months_printed_list.append(months_list)

        self.df['Months Worked'] = months_worked_list
        self.df['FTE-Adjusted Months Worked'] = fte_adjusted_months_list

        selected_columns = [
            'Cohen Clinic',
            'Name',
            'Position',
            'FTE',
            'Start Date',
            'End Date',
            'Employee Leave (start date)',
            'Employee Leave (end date)',
            'Months Worked',
            'FTE-Adjusted Months Worked'    
        ]
        return self.df[selected_columns]
    
    def add_headcount_column(self, df):
        """
        Adds a 'Headcount' column to the DataFrame. The headcount value
        appears only in the first row of the column.

        Returns:
            pd.DataFrame: Updated DataFrame with the 'Headcount' column.
        """
        try:
            # Calculate the headcount
            df = df.copy()
            headcount_value = df['FTE-Adjusted Months Worked'].sum() / 12

            # Add the 'Headcount' column with the value only in the first row
            df['Headcount'] = ""  # This adds the column to all rows
            df.loc[df.index[0], 'Headcount'] = headcount_value 

            return df
        except Exception as e:
            print(f"An error occurred while adding the headcount column: {e}")
            return None
    
    def generate_summary(self, input_dataframe, grant_year=12):
        """
        Generate a staffing summary from the input DataFrame and append the new summary columns back to it.

        Args:
        - input_dataframe (pd.DataFrame): DataFrame containing pre-calculated staffing data.

        Returns:
        - pd.DataFrame: The original DataFrame with appended summary columns.
        """
        df = input_dataframe.copy()
        roles_to_track = [
            'Regional Director', 'Clinic Director', 'Lead Clinician', 'Clinician', 
            'Prescriber', 'Front Desk/Receptionist', 'Intake', 'Case Management',
            'Office Manager', 'Outreach', 'Marketing/Communications', 
            'Data Manager', 'Intern', 'Fellow'
        ]
        try:
            # Validate input DataFrame
            self.validate_input_dataframe(df)

            # Extract the Cohen Clinic name
            clinic_name = df.iloc[0]['Cohen Clinic'] if 'Cohen Clinic' in df.columns else 'Unknown Clinic'

            summary = {
                'Cohen Clinic': clinic_name,
                'Total Staff': df['FTE-Adjusted Months Worked'].sum() / grant_year
            }

            # Role-specific headcounts for the entire grant year
            for role in roles_to_track:
                summary[f"# of {role}s"] = (
                    df.loc[df['Position'] == role, 'FTE-Adjusted Months Worked'].sum() / grant_year
                )

            summary['Leads + Clinicians'] = (
                summary.get("# of Lead Clinicians", 0) +
                summary.get("# of Clinicians", 0)
            )

            # Ensure roles default to 0 if not present
            for role in roles_to_track:
                if role not in df['Position'].unique():
                    summary[f"# of {role}s"] = 0

            # Handle missing End Date
            summary['Currently Working Count'] = df['End Date'].isna().sum()

            # Create a DataFrame from the summary
            summary_df = pd.DataFrame([summary])

            # Identify new columns in the summary that are not in the original DataFrame
            new_columns = [col for col in summary_df.columns if col not in df.columns]

            # Add new columns to the input DataFrame
            for col in new_columns:
                df[col] = None  # Initialize new column with None
                df.at[0, col] = summary_df[col].iloc[0]

            return df

        except ValueError as ve:
            raise RuntimeError(f"Validation error: {ve}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred: {e}")
