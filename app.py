import tkinter as tk
from ttkbootstrap import Style
from datetime import datetime
from ttkbootstrap.widgets import OptionMenu, Button, DateEntry
from smartsheet_fetcher import SmartsheetFetcher
from clinic_turnover import ClinicTurnover
from months_worked import MonthsWorked
from datetime import datetime, timedelta
import logging
import os

# Configure logging

log_dir = "./Logs"


# Get the current time
now = datetime.now()

# Remove log files older than 7 days
for filename in os.listdir(log_dir):
    file_path = os.path.join(log_dir, filename)
    if os.path.isfile(file_path):
        # Get the file's modification time
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        # Check if the file is older than 7 days
        if (now - file_mtime) > timedelta(days=7):
            os.remove(file_path)

# Define the base filename
base_filename = f"./Logs/log_{datetime.now().strftime('%Y-%m-%d')}"
log_filename = f"{base_filename}.log"
counter = 1

# Check if the file exists and create a new one if necessary
while os.path.exists(log_filename):
    log_filename = f"{base_filename}_{counter}.log"
    counter += 1

# Configure logging
logging.basicConfig(
    filename=log_filename,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Log all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)
def get_bearer_token(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found at {file_path}")
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("BEARER_TOKEN="):
                return line.strip().split('=', 1)[1]
    
    raise ValueError("BEARER_TOKEN not found in the config file")

# Fetch sheet names using SmartsheetFetcher
config_file_path = "./config.txt"
try:
    bearer_token = get_bearer_token(config_file_path)
    logging.info(f"Bearer token fetched successfully: {bearer_token[:4]}******")
except FileNotFoundError as fnf_error:
    logging.error(f"File not found: {fnf_error}")
except ValueError as val_error:
    logging.error(f"Error in config file: {val_error}")
except Exception as e:
    logging.critical(f"Unexpected error occurred: {e}") 

fetcher = SmartsheetFetcher(bearer_token)
all_sheets_data = fetcher.fetch_all_sheets()
sheet_names = list(all_sheets_data.keys())  

dynamic_widgets = {}  # Dictionary to store references to dynamic widgets

def show_input_fields():
    """Display input fields based on the dropdown selection."""
    # Clear existing fields in the input frame
    for widget in input_frame.winfo_children():
        widget.destroy()

    row = 0  # Initialize row index

    if dropdown.get() == "Clinic Turnover":
        # Dropdown for Sheet selection
        tk.Label(input_frame, text="Select Sheet 1:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['dropdown1'] = OptionMenu(input_frame, dropdown1, "Select Sheet", *sheet_names, bootstyle="primary")
        dynamic_widgets['dropdown1'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Select Sheet 2:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['dropdown2'] = OptionMenu(input_frame, dropdown2, "Select Sheet", *sheet_names, bootstyle="primary")
        dynamic_widgets['dropdown2'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Enter Clinic Code:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['clinic_code_entry'] = tk.Entry(input_frame, font=("Arial", 10))
        dynamic_widgets['clinic_code_entry'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Grant Start Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['grant_start_date_picker'] = DateEntry(input_frame, width=12)
        dynamic_widgets['grant_start_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Grant End Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['grant_end_date_picker'] = DateEntry(input_frame, width=12)
        dynamic_widgets['grant_end_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        # Add Date Pickers for Grant Start and End Dates
    elif dropdown.get() == "Months Worked + Staffing Ratio + Head Count":
        tk.Label(input_frame, text="Select Sheet:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['dropdown1'] = OptionMenu(input_frame, dropdown1, "Select Sheet", *sheet_names, bootstyle="primary")
        dynamic_widgets['dropdown1'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Grant Start Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['grant_start_date_picker'] = DateEntry(input_frame, width=12)
        dynamic_widgets['grant_start_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        row += 1
        tk.Label(input_frame, text="Grant End Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['grant_end_date_picker'] = DateEntry(input_frame, width=12)
        dynamic_widgets['grant_end_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)


def submit():
    selected_option = dropdown.get()
    if selected_option == "Clinic Turnover":
        sheet1 = dropdown1.get()
        sheet2 = dropdown2.get()
        clinic_code = dynamic_widgets['clinic_code_entry'].get()
        
        # Use `get()` to fetch the date as a string
        grant_start_date = dynamic_widgets['grant_start_date_picker'].entry.get()
        grant_end_date = dynamic_widgets['grant_end_date_picker'].entry.get()

        # Convert date strings to `datetime` objects if needed
        try:
            grant_start_date = datetime.strptime(grant_start_date, '%m/%d/%Y').strftime("%m-%d-%Y")
            grant_end_date = datetime.strptime(grant_end_date, '%m/%d/%Y').strftime("%m-%d-%Y")
        except ValueError as e:
            logging.error(f"Error parsing dates: {e}")
            alert_label.config(text="Invalid date format. Please select valid dates.")
            return

        if sheet1 != "Select Sheet" and sheet2 != "Select Sheet":
            sheet_id1 = all_sheets_data[sheet1]
            sheet_id2 = all_sheets_data[sheet2]
            try:
                # Fetch data for both sheets as DataFrames
                data_frame1 = fetcher.fetch_smartsheet_data(sheet_id1)
                data_frame2 = fetcher.fetch_smartsheet_data(sheet_id2)
                clinic_turnover = ClinicTurnover(data_frame1, data_frame2, clinic_code, grant_start_date, grant_end_date)
                results_df = clinic_turnover.process_data()
                create_response = fetcher.create_new_sheet("Clinic_Turnover_Calculated" + str(sheet1)[:5] + str(sheet2)[:5], results_df)
                sheet_id = create_response['result']['id']
                add_response = fetcher.add_rows_to_sheet(sheet_id, results_df)
                results_df.to_excel("Files/Clinic_Turnover_Calculated" + str(sheet1)[:5] + str(sheet2)[:5] + ".xlsx", index=False)
                alert_label.config(text="File Generated and Uploaded")
            except Exception as e:
                logging.error(f"Error processing Clinic Turnover: {e}")
                logging.debug("Detailed traceback:", exc_info=True)
                alert_label.config(text="Error processing Clinic Turnover.")
        else:
            logging.warning("Please select both sheets.")
            alert_label.config(text="Please select both sheets.")
        
    elif selected_option == "Months Worked + Staffing Ratio + Head Count":
        grant_start_date = dynamic_widgets['grant_start_date_picker'].entry.get()
        grant_end_date = dynamic_widgets['grant_end_date_picker'].entry.get()

        # Convert date strings to `datetime` objects if needed
        try:
            grant_start_date_dt = datetime.strptime(grant_start_date, '%m/%d/%Y')
            grant_end_date_dt = datetime.strptime(grant_end_date, '%m/%d/%Y')
        except ValueError as e:
            logging.error(f"Error parsing dates: {e}")
            alert_label.config(text="Invalid date format. Please select valid dates.")
            return

        sheet1 = dropdown1.get()
        
        if sheet1 != "Select Sheet":
            sheet_id1 = all_sheets_data[sheet1]
            try:
                # Fetch data for the selected sheet as a DataFrame
                data_frame1 = fetcher.fetch_smartsheet_data(sheet_id1)
                logging.info(f"Fetched data for Sheet 1 ({sheet1})")
                calculator = MonthsWorked(data_frame1, grant_start_date_dt, grant_end_date_dt)
                results_df = calculator.get_results()
                headcount_df = calculator.add_headcount_column(results_df)
                month_difference = (grant_end_date_dt.year - grant_start_date_dt.year) * 12 + grant_end_date_dt.month - grant_start_date_dt.month
                staff_summary_df = calculator.generate_summary(headcount_df, month_difference)
                create_response = fetcher.create_new_sheet("Months_Worked_Multiple_Calculated" + str(sheet_id1), staff_summary_df)
                sheet_id = create_response['result']['id']
                add_response = fetcher.add_rows_to_sheet(sheet_id, results_df)
                staff_summary_df.to_excel("Files/Months_Worked_Multiple_Calculated" + str(sheet_id1) + ".xlsx", index=False)
                alert_label.config(text="File Generated and Uploaded")
            except Exception as e:
                logging.error(f"Error processing Months Worked: {e}")
                logging.debug("Detailed traceback:", exc_info=True)
                alert_label.config(text="Error processing Months Worked.")
        else:
            logging.warning("Please select a sheet.")
            alert_label.config(text="Please select a sheet.")
    else:
        logging.warning("Invalid option selected.")
        alert_label.config(text="Invalid option selected.")

    # Clear alert after 2 seconds
    root.after(2000, lambda: alert_label.config(text=""))

root = tk.Tk()
style = Style(theme="darkly")

root.geometry("600x400")
root.title("Clinic Metrics Calculator")

style.configure("TMenubutton", font=("Arial", 10), padding=5)
style.configure("Submit.TButton", font=("Arial", 10), padding=5)

instruction_label = tk.Label(root, text="Please complete the following fields:", font=("Arial", 15), fg="white", bg=style.colors.bg)
instruction_label.pack(pady=(20, 5))

# Main dropdown
dropdown = tk.StringVar(value="Select an option")
dropdown1 = tk.StringVar(value="Select Sheet")
dropdown2 = tk.StringVar(value="Select Sheet")

# Define input_frame globally before creating dependent widgets
input_frame = tk.Frame(root, bg=style.colors.bg)
input_frame.pack(fill="x", pady=10)

# Input fields for Clinic Turnover
clinic_code_entry = tk.Entry(input_frame, font=("Arial", 10))

# Initialize DateEntry widgets without the font parameter
grant_start_date_picker = DateEntry(input_frame, width=12)
grant_end_date_picker = DateEntry(input_frame, width=12)

# Attach the trace_add callback after input_frame is defined
dropdown.trace_add("write", lambda *args: show_input_fields())  # Trigger on dropdown change
OptionMenu(root, dropdown, "Select an option", "Clinic Turnover", "Months Worked + Staffing Ratio + Head Count", bootstyle="primary").pack(pady=5)

# Alert label for feedback
alert_label = tk.Label(root, text="", font=("Arial", 10), fg="green", bg=style.colors.bg)
alert_label.pack(pady=(5, 0))

submit_button = Button(root, text="Submit", command=submit, width=10, style="Submit.TButton")
submit_button.pack(pady=20)

root.mainloop()
