import json
import os

import numpy as np

import pandas as pd
from utils.table_to_html import table_to_html
from django.shortcuts import HttpResponse, render

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file is part of the request
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Read the file into a DataFrame
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.filename.endswith('.xlsx'):
                    df = pd.read_excel(file)

                # Process the data and prepare summaries
                num_rows = df.shape[0]
                num_columns = df.shape[1]
                column_names = ', '.join(df.columns)
                summary = f"Number of rows: {num_rows}\nNumber of columns: {num_columns}\nColumn names: {column_names}\n"
                
                return render_template('index.html', summary=summary)
            except Exception as e:
                return f"An error occurred: {e}"

    return render_template('index.html', summary=None)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

if __name__ == '__main__':
    app.run(debug=True)
















def calculate_growth(Value_2024, Value_2023):
    if Value_2024 == 0 and Value_2023 > 0:
        return -1  # Negative growth using 2023 as reference
    elif Value_2024 > 0 and Value_2023 == 0:
        return 1  # Growth using 2024 as reference
    elif Value_2024 == 0 and Value_2023 == 0:
        return 0  # 0 growth when both are 0
    else:
        return (Value_2024 - Value_2023) / Value_2023
    
def create_summary(data, filter_values):
    summary = {
        "filter_values": filter_values,
        "Average of RAROC": str(round(data["RAROC"].mean(), 2)),
        "Average of ROE": str(round(data["ROE"].mean(), 2)),
        "Sum of Disbursed Amount": str(round(data["DisbursedAmount"].sum(), 2)),
        "Sum of Outstanding Balance": str(round(data["OutstandingBalance"].sum(), 2)),
        "Average of Processing Fee": str(round(data["ProcessingFee"].mean(), 2)),
        "Sum of Restructed Amount": str(round(data["RestructedAmount"].sum(), 2)),
        "Sum of Written off Amount": str(round(data["WrittenoffAmount"].sum(), 2))
    }
    
    return summary

def index(request):
    context = {}
    return render(request, "Dashboard/index.html", context)

def main_func(request):
    if request.method == "POST":
        context = {}
        request_data = request.POST
        print(request_data)
        func = request_data["func"]
        options = {}
        
        if func == "fetch_data":
            input_data_file = request.FILES['file']
            print(input_data_file)
            
            input_data_workbook = pd.ExcelFile(input_data_file)
            
            global input_data
            input_data = pd.read_excel(input_data_workbook)
            
            
            Age_conditions = [
                input_data["Age"] < 18,
                input_data["Age"].between(18, 35),
                input_data["Age"].between(36, 55),
                input_data["Age"].between(56, 65),
                input_data["Age"] > 65
            ]
            Age_choices = [
                "Under 18",
                "18-35",
                "36-55",
                "56-65",
                "Over 65"
            ]

            # Define conditions and choices for Interest Rate Range
            input_data["Rate of Interest"] = input_data["Rate of Interest"] / 100  # Convert to decimal
            ROI_conditions = [
                (input_data["Rate of Interest"] > 0) & (input_data["Rate of Interest"] <= 0.03),
                (input_data["Rate of Interest"] > 0.03) & (input_data["Rate of Interest"] <= 0.06),
                (input_data["Rate of Interest"] > 0.06) & (input_data["Rate of Interest"] <= 0.09),
                (input_data["Rate of Interest"] > 0.09) & (input_data["Rate of Interest"] <= 0.12),
                (input_data["Rate of Interest"] > 0.12) & (input_data["Rate of Interest"] <= 0.15)
            ]
            ROI_choices = [
                ">0-<=3%",
                ">3-<=6%",
                ">6-<=9%",
                ">9-<=12%",
                ">12-<=15%"
            ]

            # Define conditions and choices for PD score / Behavioral Score Category
            PD_conditions = [
                input_data["PD score / behavioral score "] == 1,
                input_data["PD score / behavioral score "] == 2,
                input_data["PD score / behavioral score "] == 3,
                input_data["PD score / behavioral score "] == 4,
                input_data["PD score / behavioral score "] == 5
            ]
            PD_choices = [
                "Best (1)",
                "Good (2)",
                "Fair (3)",
                "Moderate (4)",
                "Poor (5)"
            ]
            default_PD_choice = "Unknown"
            
            input_data["Age Category"] = np.select(Age_conditions, Age_choices)
            input_data["Formatted_Rate_of_Interest"] = (input_data["Rate of Interest"] * 100).apply(lambda x: "{:.2f}%".format(x))
            input_data["Interest Rate Range"] = np.select(ROI_conditions, ROI_choices)
            input_data["PD score / behavioral Score Category"] = np.select(PD_conditions, PD_choices, default=default_PD_choice)
            
            global filters
            filters = input_data.columns
            
            options_filters = "<option value="" selected>Select Category</option>"
            for col in filters:
                col_withoutspace = col.replace(" ", "")
                options_filters += f"<option value = {col_withoutspace}>{col}</option>"

            
            disbursement_2023 = input_data[input_data["Date"] == "31/3/2023"].groupby('Loan Type')['Disbursed Amount'].sum()
            disbursement_2024 = input_data[input_data["Date"] == "31/3/2024"].groupby('Loan Type')['Disbursed Amount'].sum()

            # Combine the two Series into a DataFrame
            disbursement_combined = pd.DataFrame({
                '2023': disbursement_2023,
                '2024': disbursement_2024
            }).fillna(0)  # Fill NaN with 0 for loan types not present in both years

            # Calculate growth for each loan type
            disbursement_combined['Growth'] = disbursement_combined.apply(
                lambda row: calculate_growth(row['2024'], row['2023']), axis=1)

            # Create dictionary for plotting
            disbursement_line = {
                "x": list(disbursement_combined.index),
                "y": list(disbursement_combined["Growth"])
            }
            
            disbursement_total = input_data.groupby('Loan Type')['Disbursed Amount'].sum()
            disbursement_total = disbursement_total.astype(float)
            print(disbursement_total)
            disbursement_pie = {
                "labels":list(disbursement_total.index),
                "values":list(disbursement_total.values)
            }
            
            string = f"<h4> Total Disbursement (in millon) {sum(np.array(disbursement_total.values))/1000000} </h4> <br><br> <h4>Total Customers {len(input_data)}</h4>"
            
            #filtering the NPA rows
            npa_data = input_data[input_data['Delinquency Status (STD/SMA-1/SMA-2/NPA)'] == 'NPA']
            npa_2023 = npa_data[npa_data["Date"] == "31/3/2023"].groupby('Loan Type')['Outstanding Balance'].sum()
            npa_2024 = npa_data[npa_data["Date"] == "31/3/2024"].groupby('Loan Type')['Outstanding Balance'].sum()
            
            npa_combined = pd.DataFrame({
                '2023': npa_2023,
                '2024': npa_2024
            }).fillna(0)  # Fill NaN with 0 for loan types not present in both years
            
            npa_combined['Growth'] = npa_combined.apply(
                lambda row: calculate_growth(row['2024'], row['2023']), axis=1)
            
            npa_line = {
                "x": list(npa_combined.index),
                "y": list(npa_combined["Growth"])
            }
            
            npa_total = npa_data.groupby('Loan Type')['Outstanding Balance'].sum()
            npa_total = npa_total.astype(float)

            npa_pie = {
                "labels":list(npa_total.index),
                "values":list(npa_total.values)
            }
            
            string_1 = f"<h4> Total NPA Amount (in millon) {sum(np.array(npa_total.values))/1000000} </h4> <br><br> <h4>Total Customers {len(npa_data)}</h4>"
            
            
            input_data.columns = input_data.columns.str.replace(' ', '')
            
            input_data_summary = {
                "Average of RAROC": round(input_data["RAROC"].mean(), 2),
                "Average of ROE": round(input_data["ROE"].mean(),2),
                "Sum of Disbursed Amount": round(input_data["DisbursedAmount"].sum(),2),
                "Sum of Outstanding Balance": round(input_data["OutstandingBalance"].sum(),2),
                "Average of Processing Fee": round(input_data["ProcessingFee"].mean(),2),
                "Sum of Restructed Amount": round(input_data["RestructedAmount"].sum(),2),
                "Sum of Written off Amount": round(input_data["WrittenoffAmount"].sum(),2)
            }

            # Converting final_data dictionary to a DataFrame with an index
            input_data_df = pd.DataFrame(input_data_summary, index=[0])
            print(input_data_df)
                        
            input_table = table_to_html(input_data_df,columns=input_data_df.columns)
            
            options["disbursement_line"] = disbursement_line 
            options["disbursement_pie"] = disbursement_pie
            options["disbursement_summary"] = string
            
            options["risk_line"] = npa_line
            options["risk_pie"] = npa_pie
            options["risk_summary"] = string_1
            
            options["input_table"] = input_table
            
            options["filter_1"] = options_filters
            context["options"] = options
            
        elif func == "populate_filter_val1":
            filter_1 = request_data["filter_1_value"]
            unique_values_1 = input_data[filter_1].unique()
            print(unique_values_1)
            
            string = "<option value="" selected>Select Value</option>"
            for col in unique_values_1:
                print(type(col))
                if isinstance(col, np.int64):
                    col_withoutspace = float(col)
                else:
                    col_withoutspace = col.replace(" ", "")
                    print(col_withoutspace)
                string += f"<option value='{col_withoutspace}'>{col}</option>"
            
            options["values_1"] = string
            context["options"] = options

            
        elif func == "populate_filter2":
            filter_1 = request_data["filter_1_value"]
            filter_val1 = request_data["filter_1_filtering"]
            
            index_to_remove = None
            for index, value in enumerate(filters):
                if value.replace(" ", "") == filter_1:
                    index_to_remove = index
                    break
            filters = list(filters)
            
            if index_to_remove is not None:
                filters.pop(index_to_remove)
            
            global input_data_1
            
            try:
                input_data_1 = input_data[input_data[filter_1] == float(filter_val1)]
            except:
                input_data_1 = input_data[input_data[filter_1].str.replace(" ", "").str.contains(filter_val1, case=False)]
            
            string ="<option value="" selected>Select Category</option>"
            for col in filters:
                col_withoutspace = col.replace(" ", "")
                string += f"<option value = {col_withoutspace}>{col}</option>"
            options["filter_2"] = string
            context["options"] = options

        elif func == "populate_filter_val2":
            filter_2 = request_data["filter_2_value"]
            unique_values_2 = input_data_1[filter_2].unique()
            
            string = "<option value="" selected>Select Value</option>"
            for col in unique_values_2:
                if isinstance(col, np.int64):
                    col_withoutspace = float(col)
                else:
                    col_withoutspace = col.replace(" ", "")
                string += f"<option value = {str(col_withoutspace)}>{col}</option>"
            
            options["values_2"] = string
            context["options"] = options
            
        elif func == "populate_filter3":
            filter_2 = request_data["filter_2_value"]
            filter_val2 = request_data["filter_2_filtering"]
            
            
            index_to_remove = None
            for index, value in enumerate(filters):
                if value.replace(" ", "") == filter_2:
                    index_to_remove = index
                    break
            if index_to_remove is not None:
                filters.pop(index_to_remove)
            
            global input_data_2
            try:
                input_data_2 = input_data_1[input_data_1[filter_2] == float(filter_val2)]
            except:
                input_data_2 = input_data_1[input_data_1[filter_2].str.replace(" ", "").str.contains(filter_val2, case=False)]
            
            string ="<option value="" selected>Select Category</option>"
            for col in filters:
                col_withoutspace = col.replace(" ", "")
                string += f"<option value = {col_withoutspace}>{col}</option>"
            options["filter_3"] = string
            context["options"] = options

        elif func == "populate_filter_val3":
            filter_3 = request_data["filter_3_value"]
            unique_values_3 = input_data_2[filter_3].unique()
            
            string = "<option value="" selected>Select Value</option>"
            for col in unique_values_3:
                if isinstance(col, np.int64):
                    col_withoutspace = float(col)
                else:
                    col_withoutspace = col.replace(" ", "")
                string += f"<option value = {str(col_withoutspace)}>{col}</option>"
            
            options["values_3"] = string
            context["options"] = options
            
        elif func == "decompositionchart_tree":
            filter_1 = request_data["filter_1"]
            filter_2 = request_data["filter_2"]
            filter_3 = request_data["filter_3"]
            
            filter_1_val = request_data["filter_1_val"]
            filter_2_val = request_data["filter_2_val"]
            filter_3_val = request_data["filter_3_val"]

            # Initialize the tree structure
            tree = {
                'name': filter_1,
                'children': [],
                'summary': create_summary(input_data, [filter_1])
            }

            # Level 1: Iterate over unique values of filter_1
            for value1 in input_data[filter_1].unique():
                data_level_1 = input_data[input_data[filter_1] == value1]
                try:
                    value1 = float(value1)
                except:
                    value1 = value1
                children1 = {
                    'name': value1,
                    'children': [],
                    'summary': create_summary(data_level_1, [filter_1, value1])
                }
                
                # Level 2: Iterate over unique values of filter_2 within filter_1 data
                for value2 in data_level_1[filter_2].unique():
                    data_level_2 = data_level_1[data_level_1[filter_2] == value2]
                    try:
                        value2 = float(value2)
                    except:
                        value2 = value2
                    children2 = {
                        'name': value2,
                        'children': [],
                        'summary': create_summary(data_level_2, [filter_1, value1, filter_2, value2])
                    }
                    
                    # Level 3: Iterate over unique values of filter_3 within filter_1 and filter_2 data
                    for value3 in data_level_2[filter_3].unique():
                        data_level_3 = data_level_2[data_level_2[filter_3] == value3]
                        try:
                            value3 = float(value3)
                        except:
                            value3 = value3
                        children3 = {
                            'name': value3,
                            'summary': create_summary(data_level_3, [filter_1, value1, filter_2, value2, filter_3, value3])
                        }
                        children2['children'].append(children3)
                    
                    children1['children'].append(children2)
                
                tree['children'].append(children1)

                    
            global summarized_table
            try:
                summarized_table = input_data_2[input_data_2[filter_3] == float(filter_3_val)]
            except:
                summarized_table = input_data_2[input_data_2[filter_3].str.replace(" ", "").str.contains(filter_3_val, case=False)]
               
            print(summarized_table.columns)
            
            final_data = {
                "Average of RAROC": round(summarized_table["RAROC"].mean(), 2),
                "Average of ROE": round(summarized_table["ROE"].mean(),2),
                "Sum of Disbursed Amount": round(summarized_table["DisbursedAmount"].sum(),2),
                "Sum of Outstanding Balance": round(summarized_table["OutstandingBalance"].sum(),2),
                "Average of Processing Fee": round(summarized_table["ProcessingFee"].mean(),2),
                "Sum of Restructed Amount": round(summarized_table["RestructedAmount"].sum(),2),
                "Sum of Written off Amount": round(summarized_table["WrittenoffAmount"].sum(),2)
            }

            # Converting final_data dictionary to a DataFrame with an index
            final_data_df = pd.DataFrame(final_data, index=[0])
            print(final_data_df)
                        
            final_table = table_to_html(final_data_df,columns=final_data_df.columns)
            
            disbursement_2023 = summarized_table[summarized_table["Date"] == "31/3/2023"].groupby('LoanType')['DisbursedAmount'].sum()
            disbursement_2024 = summarized_table[summarized_table["Date"] == "31/3/2024"].groupby('LoanType')['DisbursedAmount'].sum()

            # Combine the two Series into a DataFrame
            disbursement_combined = pd.DataFrame({
                '2023': disbursement_2023,
                '2024': disbursement_2024
            }).fillna(0)  # Fill NaN with 0 for loan types not present in both years

            # Calculate growth for each loan type
            disbursement_combined['Growth'] = disbursement_combined.apply(
                lambda row: calculate_growth(row['2024'], row['2023']), axis=1)

            # Create dictionary for plotting
            disbursement_line = {
                "x": list(disbursement_combined.index),
                "y": list(disbursement_combined["Growth"])
            }
            
            disbursement_total = summarized_table.groupby('LoanType')['DisbursedAmount'].sum()
            disbursement_total = disbursement_total.astype(float)
            print(disbursement_total)
            disbursement_pie = {
                "labels":list(disbursement_total.index),
                "values":list(disbursement_total.values)
            }
            
            string = f"<h4> Total Disbursement (in millon) {sum(np.array(disbursement_total.values))/1000000} </h4> <br><br> <h4>Total Customers {len(summarized_table)}</h4>"
            
            #filtering the NPA rows
            npa_data = summarized_table[summarized_table['DelinquencyStatus(STD/SMA-1/SMA-2/NPA)'] == 'NPA']
            npa_2023 = npa_data[npa_data["Date"] == "31/3/2023"].groupby('LoanType')['OutstandingBalance'].sum()
            npa_2024 = npa_data[npa_data["Date"] == "31/3/2024"].groupby('LoanType')['OutstandingBalance'].sum()
            
            npa_combined = pd.DataFrame({
                '2023': npa_2023,
                '2024': npa_2024
            }).fillna(0)  # Fill NaN with 0 for loan types not present in both years
            
            npa_combined['Growth'] = npa_combined.apply(
                lambda row: calculate_growth(row['2024'], row['2023']), axis=1)
            
            npa_line = {
                "x": list(npa_combined.index),
                "y": list(npa_combined["Growth"])
            }
            
            npa_total = npa_data.groupby('LoanType')['OutstandingBalance'].sum()
            npa_total = npa_total.astype(float)

            npa_pie = {
                "labels":list(npa_total.index),
                "values":list(npa_total.values)
            }
            
            string_1 = f"<h4> Total NPA Amount (in millon) {sum(np.array(npa_total.values))/1000000} </h4> <br><br> <h4>Total Customers {len(npa_data)}</h4>"
            
            
            options["disbursement_line"] = disbursement_line 
            options["disbursement_pie"] = disbursement_pie
            options["disbursement_summary"] = string
            
            options["risk_line"] = npa_line
            options["risk_pie"] = npa_pie
            options["risk_summary"] = string_1
            
            print(final_table)        
            options["tree"] = tree
            context["options"] = options
            context["final_table"] = final_table
            
    return HttpResponse(json.dumps(context))
