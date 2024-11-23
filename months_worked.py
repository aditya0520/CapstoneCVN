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

        
        print("DF SHAPE IS ", self.df.shape)
        file_path = "Current_output.xlsx"  
        self.df.to_excel(file_path, index=False)

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

        self.df['Months Worked (Custom)'] = months_worked_list
        self.df['FTE-Adjusted Months Worked (Custom)'] = fte_adjusted_months_list

        selected_columns = [
            'Cohen Clinic',
            'Name',
            'Position',
            'FTE',
            'Start Date',
            'End Date',
            'Employee Leave (start date)',
            'Employee Leave (end date)',
            'Months Worked (Custom)',
            'FTE-Adjusted Months Worked (Custom)'    
        ]
        return self.df[selected_columns]

