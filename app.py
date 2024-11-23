import tkinter as tk
from ttkbootstrap import Style
from datetime import datetime
from ttkbootstrap.widgets import OptionMenu, Button, DateEntry
from smartsheet_fetcher import SmartsheetFetcher
from clininc_turnover import ClinicTurnover
from staffing_summary import StaffingSummary
from months_worked import MonthsWorked

# Fetch sheet names using SmartsheetFetcher
bearer_token = 'hhQ21NI9mu4JzKmskRS19wfiY7lX4smNGDUAo'
fetcher = SmartsheetFetcher(bearer_token)
all_sheets_data = fetcher.fetch_all_sheets()
sheet_names = list(all_sheets_data.keys())  # Convert to a list for indexing

dynamic_widgets = {}  # Dictionary to store references to dynamic widgets

def show_input_fields():
    """Display input fields based on the dropdown selection."""
    # Clear existing fields in the input frame
    for widget in input_frame.winfo_children():
        widget.destroy()

    row = 0  # Initialize row index

    if dropdown.get() in ["Clinic Turnover", "Months Worked", "Staffing Ratio"]:
        # Dropdown for Sheet selection
        tk.Label(input_frame, text="Select Sheet:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        dynamic_widgets['dropdown1'] = OptionMenu(input_frame, dropdown1, "Select Sheet", *sheet_names, bootstyle="primary")
        dynamic_widgets['dropdown1'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        # For "Clinic Turnover," add additional fields
        if dropdown.get() == "Clinic Turnover":
            row += 1
            tk.Label(input_frame, text="Select Sheet 2:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            dynamic_widgets['dropdown2'] = OptionMenu(input_frame, dropdown2, "Select Sheet 2", *sheet_names, bootstyle="primary")
            dynamic_widgets['dropdown2'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

            row += 1
            tk.Label(input_frame, text="Enter Clinic Code:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            dynamic_widgets['clinic_code_entry'] = tk.Entry(input_frame, font=("Arial", 10))
            dynamic_widgets['clinic_code_entry'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        # Add Date Pickers for Grant Start and End Dates
        if dropdown.get() in ["Clinic Turnover", "Months Worked"]:
            row += 1
            tk.Label(input_frame, text="Grant Start Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            dynamic_widgets['grant_start_date_picker'] = DateEntry(input_frame, width=12)
            dynamic_widgets['grant_start_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

            row += 1
            tk.Label(input_frame, text="Grant End Date:", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            dynamic_widgets['grant_end_date_picker'] = DateEntry(input_frame, width=12)
            dynamic_widgets['grant_end_date_picker'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        # For "Staffing Ratio," add a field for Duration (months)
        if dropdown.get() == "Staffing Ratio":
            row += 1
            tk.Label(input_frame, text="Enter Duration (months):", font=("Arial", 12), fg="white", bg=style.colors.bg).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            dynamic_widgets['duration_entry'] = tk.Entry(input_frame, font=("Arial", 10))
            dynamic_widgets['duration_entry'].grid(row=row, column=1, sticky="ew", padx=10, pady=5)



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
            grant_start_date = datetime.strptime(grant_start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            grant_end_date = datetime.strptime(grant_end_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            alert_label.config(text="Invalid date format. Please select valid dates.")
            return

        if sheet1 != "Select Sheet 1" and sheet2 != "Select Sheet 2":
            sheet_id1 = all_sheets_data[sheet1]
            sheet_id2 = all_sheets_data[sheet2]
            try:
                # Fetch data for both sheets as DataFrames
                data_frame1 = fetcher.fetch_smartsheet_data(sheet_id1)
                data_frame2 = fetcher.fetch_smartsheet_data(sheet_id2)
                alert_label.config(text="Data submitted successfully!")
            except Exception as e:
                print(f"Error fetching sheets: {e}")
                alert_label.config(text="Error fetching sheets.")
            
            clinic_turnover = ClinicTurnover(data_frame1, data_frame2, clinic_code, grant_start_date, grant_end_date)
            results_df = clinic_turnover.process_data()

            print(results_df.head())
        else:
            print("Please select both sheets.")
            alert_label.config(text="Please select both sheets.")
        
    elif selected_option == "Months Worked":
        grant_start_date = dynamic_widgets['grant_start_date_picker'].entry.get()
        grant_end_date = dynamic_widgets['grant_end_date_picker'].entry.get()

        # Convert date strings to `datetime` objects if needed
        try:
            grant_start_date = datetime.strptime(grant_start_date, '%m/%d/%Y')
            grant_end_date = datetime.strptime(grant_end_date, '%m/%d/%Y')
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            alert_label.config(text="Invalid date format. Please select valid dates.")
            return

        sheet1 = dropdown1.get()
        
        if sheet1 != "Select Sheet 1":
            sheet_id1 = all_sheets_data[sheet1]
            try:
                # Fetch data for the selected sheet as a DataFrame
                data_frame1 = fetcher.fetch_smartsheet_data(sheet_id1)
                print(f"Fetched data for Sheet 1 ({sheet1}):")
                print(data_frame1.head())
            except Exception as e:
                print(f"Error fetching sheet: {e}")
            
        calculator = MonthsWorked(data_frame1, grant_start_date, grant_end_date)
        results_df = calculator.get_results()
        print(results_df.head)
        results_df.to_excel('months_worked.xlsx', index=False)
        alert_label.config(text="File Generated!")
        
    elif selected_option == "Staffing Ratio":
        sheet1 = dropdown1.get()
        duration_months = dynamic_widgets['duration_entry'].get()

        try:
            # Ensure duration is a valid integer
            duration_months = int(duration_months)
        except ValueError:
            print("Invalid duration. Please enter a valid number.")
            alert_label.config(text="Invalid duration. Please enter a valid number.")
            return

        if sheet1 != "Select Sheet":
            sheet_id1 = all_sheets_data[sheet1]
            try:

                data_frame1 = fetcher.fetch_smartsheet_data(sheet_id1)
                print(f"Fetched data for Sheet 1 ({sheet1}):")
                print(data_frame1.head())


                # calculator = StaffingSummary(grant_year=duration_months)
                # summary_df = calculator.generate_summary(data_frame1)

                # summary_df.to_excel('staffing_ratio.xlsx', index=False)
                # print(summary_df.head())
                # alert_label.config(text="Staffing Ratio File Generated!")
            except Exception as e:
                print(f"Error fetching sheet: {e}")
                alert_label.config(text="Error fetching sheet.")

            
            calculator = StaffingSummary(grant_year=duration_months)
            summary_df = calculator.generate_summary(data_frame1)

            summary_df.to_excel('staffing_ratio.xlsx', index=False)
            print(summary_df.head())
            alert_label.config(text="Staffing Ratio File Generated!")
        
        else:
            print("Please select a sheet.")
            alert_label.config(text="Please select a sheet.")
        
    
    else:
        print("Please select a valid option.")
        alert_label.config(text="Invalid option.")

    # Clear alert after 2 seconds
    root.after(2000, lambda: alert_label.config(text=""))




root = tk.Tk()
style = Style(theme="darkly")

root.geometry("600x400")
root.title("Dynamic Input Fields")

style.configure("TMenubutton", font=("Arial", 10), padding=5)
style.configure("Submit.TButton", font=("Arial", 10), padding=5)

instruction_label = tk.Label(root, text="Please select the Sheet:", font=("Arial", 15), fg="white", bg=style.colors.bg)
instruction_label.pack(pady=(20, 5))

# Main dropdown
dropdown = tk.StringVar(value="Select an option")
dropdown1 = tk.StringVar(value="Select Sheet 1")
dropdown2 = tk.StringVar(value="Select Sheet 2")

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
OptionMenu(root, dropdown, "Select Action", "Clinic Turnover", "Months Worked", "Staffing Ratio", bootstyle="primary").pack(pady=5)

# Alert label for feedback
alert_label = tk.Label(root, text="", font=("Arial", 10), fg="green", bg=style.colors.bg)
alert_label.pack(pady=(5, 0))

submit_button = Button(root, text="Submit", command=submit, width=10, style="Submit.TButton")
submit_button.pack(pady=20)

root.mainloop()