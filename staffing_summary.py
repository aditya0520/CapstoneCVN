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

    def generate_summary(self, input_dataframe):
        """
        Generate a staffing summary from the input DataFrame.

        Args:
        - input_dataframe (pd.DataFrame): DataFrame containing pre-calculated staffing data.

        Returns:
        - pd.DataFrame: A DataFrame with the staffing summary.
        """
        df = input_dataframe.copy()

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

    def save_to_excel(self, summary_dataframe, output_file):
        """
        Save the summary DataFrame to an Excel file.

        Args:
        - summary_dataframe (pd.DataFrame): DataFrame containing the staffing summary.
        - output_file (str): Path to save the Excel file.
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_dataframe.to_excel(writer, sheet_name='Summary', index=False)
        print(f"Summary saved to {output_file}")


