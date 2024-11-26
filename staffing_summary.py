import pandas as pd

class StaffingSummary:
    def __init__(self, grant_year=12):
        """
        Initialize the StaffingSummaryGenerator.

        Args:
        - grant_year (int): Number of months in the grant year (default is 12).
        """
        self.grant_year = grant_year
        self.roles_to_track = [
            'Regional Director', 'Clinic Director', 'Lead Clinician', 'Clinician', 
            'Prescriber', 'Front Desk/Receptionist', 'Intake', 'Case Management',
            'Office Manager', 'Outreach', 'Marketing/Communications', 
            'Data Manager', 'Intern', 'Fellow'
        ]

    def validate_input_dataframe(self, df):
        """
        Validate the input DataFrame for required columns, datatypes, and values.

        Args:
        - df (pd.DataFrame): The input DataFrame to validate.

        Raises:
        - ValueError: If required columns are missing or datatypes/values are invalid.
        """
        # Check for missing columns
        required_columns = ['Position', 'Months Worked (FTE Adjusted)', 'End Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)} in the input data.")

        # Check for empty dataset
        if df.empty:
            raise ValueError("The input DataFrame is empty. Please provide valid data.")

        # Validate datatypes
        if not pd.api.types.is_numeric_dtype(df['Months Worked (FTE Adjusted)']):
            raise ValueError("'Months Worked (FTE Adjusted)' must be a numeric column.")

        if not pd.api.types.is_string_dtype(df['Position']):
            raise ValueError("'Position' must be a string column.")

        if not (pd.api.types.is_datetime64_any_dtype(df['End Date']) or not pd.api.types.is_string_dtype(df['End Date'])):
            raise ValueError("'End Date' must be a datetime or string column.")

        # Check for negative or missing values in key columns
        if (df['Months Worked (FTE Adjusted)'] < 0).any():
            raise ValueError("'Months Worked (FTE Adjusted)' contains negative values.")

        if df['Position'].isnull().any():
            raise ValueError("The 'Position' column contains missing values.")

        # Check for duplicates
        if df.duplicated().any():
            raise ValueError("The input DataFrame contains duplicate rows.")

    def generate_summary(self, input_dataframe):
        """
        Generate a staffing summary from the input DataFrame.

        Args:
        - input_dataframe (pd.DataFrame): DataFrame containing pre-calculated staffing data.

        Returns:
        - pd.DataFrame: A DataFrame with the staffing summary.
        """
        df = input_dataframe.copy()
        try:
            # Validate input DataFrame
            self.validate_input_dataframe(df)

            # Extract the Cohen Clinic name
            clinic_name = df.iloc[0]['Cohen Clinic'] if 'Cohen Clinic' in df.columns else 'Unknown Clinic'

            summary = {
                'Cohen Clinic': clinic_name,
                'Total Staff': df['Months Worked (FTE Adjusted)'].sum() / self.grant_year
            }

            # Role-specific headcounts for the entire grant year
            for role in self.roles_to_track:
                summary[f"# of {role}s"] = (
                    df.loc[df['Position'] == role, 'Months Worked (FTE Adjusted)'].sum() / self.grant_year
                )

            summary['Leads + Clinicians'] = (
                summary.get("# of Lead Clinicians", 0) +
                summary.get("# of Clinicians", 0)
            )

            # Ensure roles default to 0 if not present
            for role in self.roles_to_track:
                if role not in df['Position'].unique():
                    summary[f"# of {role}s"] = 0

            # Handle missing End Date
            summary['Currently Working Count'] = df['End Date'].isna().sum()

            return pd.DataFrame([summary])

        except ValueError as ve:
            raise RuntimeError(f"Validation error: {ve}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred: {e}")
