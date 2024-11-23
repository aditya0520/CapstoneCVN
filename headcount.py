import pandas as pd

class Headcount:
    """
    A class to process a DataFrame and add a 'Headcount' column
    with the headcount value appearing only in the first row.
    """
    def __init__(self, df):
        """
        Initialize the processor with a DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame to process.
        """
        self.df = df

    def add_headcount_column(self):
        """
        Adds a 'Headcount' column to the DataFrame. The headcount value
        appears only in the first row of the column.

        Returns:
            pd.DataFrame: Updated DataFrame with the 'Headcount' column.
        """
        try:
            # Calculate the headcount
            headcount_value = self.df['Months Worked (FTE Adjusted)'].sum() / 12

            # Add the 'Headcount' column with the value only in the first row
            self.df['Headcount'] = ""
            self.df.at[0, 'Headcount'] = headcount_value

            return self.df
        except Exception as e:
            print(f"An error occurred while adding the headcount column: {e}")
            return None
