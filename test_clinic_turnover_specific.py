import pandas as pd
from clinic_turnover import ClinicTurnover

def create_specific_test_data():
    """
    Creates specific test data for 2023 and 2024 as per the user's provided data.
    
    Returns:
        tuple: A tuple containing two pandas DataFrames for the previous and current year.
    """
    # Data for 2023
    data_prev_year = {
        'Primary Column': [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        'Month #': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        '# Separated Employees': [0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0],
        'Avg # Employees': [11, 12, 12, 12, 10, 10, 10, 10, 10, 11, 10, 11],
        'Turnover': [0.00, 0.00, 0.00, 0.00, 0.20, 0.00, 0.00, 0.00, 0.10, 0.00, 0.00, 0.00],
        'Month Start': [
            '2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01',
            '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01',
            '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01'
        ],
        'Month End': [
            '2023-01-31', '2023-02-28', '2023-03-31', '2023-04-30',
            '2023-05-31', '2023-06-30', '2023-07-31', '2023-08-31',
            '2023-09-30', '2023-10-31', '2023-11-30', '2023-12-31'
        ]
    }
    df_prev_year = pd.DataFrame(data_prev_year)

    # Data for 2024
    data_curr_year = {
        'Primary Column': [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        'Month #': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        '# Separated Employees': [0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0],
        'Avg # Employees': [11, 12, 12, 12, 10, 10, 10, 10, 10, 11, 11, 11],
        'Turnover': [0.00, 0.00, 0.00, 0.00, 0.20, 0.00, 0.00, 0.00, 0.10, 0.00, 0.00, 0.00],
        'Month Start': [
            '2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01',
            '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01',
            '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01'
        ],
        'Month End': [
            '2024-01-31', '2024-02-29', '2024-03-31', '2024-04-30',
            '2024-05-31', '2024-06-30', '2024-07-31', '2024-08-31',
            '2024-09-30', '2024-10-31', '2024-11-30', '2024-12-31'
        ]
    }
    df_curr_year = pd.DataFrame(data_curr_year)

    return df_prev_year, df_curr_year

def main():
    # Create the specific test data
    df_prev_year, df_curr_year = create_specific_test_data()

    # Define parameters
    clinic_code = 'CS'
    grant_start_date = '2023-11-01'
    grant_end_date = '2024-10-31'

    # faulty gy date
    # clinic_code = 'CS'
    # grant_start_date = '11-01'
    # grant_end_date = '10-31'

    # Initialize ClinicTurnover
    try:
        clinic_turnover = ClinicTurnover(
            df_prev_year=df_prev_year,
            df_curr_year=df_curr_year,
            clinic_code=clinic_code,
            grant_start_date=grant_start_date,
            grant_end_date=grant_end_date
        )
        print("Initialization successful.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    # Process data
    try:
        processed_data = clinic_turnover.process_data()
        print("Data processing successful.")
        print(processed_data)
    except Exception as e:
        print(f"Data processing failed: {e}")
        return

    # Optionally, save the processed data to Excel
    try:
        output_filename = f"Clinic Turnover GY2 - {clinic_code}.xlsx"
        processed_data.to_excel(output_filename, index=False)
        print(f"Processed data saved to {output_filename}")
    except Exception as e:
        print(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    main()