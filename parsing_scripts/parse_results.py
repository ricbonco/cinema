import pandas as pd
from datetime import datetime
import numpy as np
import sys, os

df = pd.DataFrame(columns = ['Operation', 'Min', 'Max', 'Mean', 'Std', 'Var', 'CoV'])
# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('Summary.xlsx', engine='xlsxwriter')

if len(sys.argv) == 2:
    directory = sys.argv[1] 
else:
    directory = os.getcwd()

files = os.listdir(directory)
files_to_process = [f'{directory}/{f}' for f in files if os.path.isfile(directory+'/'+f) and ".xlsx" in f] #Filtering only the files.
# Ricardo print(files_to_process)

for file in files_to_process:

    excel_data_df = pd.read_excel(file, sheet_name='Sheet1')

    operations_list = list(dict.fromkeys(excel_data_df['Operation'].tolist()))
    measurements_list = []
    for element in operations_list:
        measurements_list.append(element.replace("_start", "").replace("_end", ""))

    measurements_list = list(dict.fromkeys(measurements_list))

    # Ricardo print(f'measurements_list {measurements_list}')

    for measurement in measurements_list:

        # Ricardo print(f"*** measurement {measurement}")

        df_start = excel_data_df.loc[excel_data_df['Operation'] == f"{measurement}_start"]
        df_end = excel_data_df.loc[excel_data_df['Operation'] == f"{measurement}_end"]

        time_list = []

        df_start_list = df_start['Time'].tolist()
        df_end_list = df_end['Time'].tolist()

        # Ricardo print(f'len start {len(df_start_list)} len end {len(df_end_list)} ')

        for i in range(len(df_start_list)):
            time_list.append(pd.to_datetime(df_end_list[i]) - pd.to_datetime(df_start_list[i]))

        df_duration = pd.DataFrame (time_list, columns = ['Duration'])

        df_duration['new'] = df_duration['Duration'].values.astype(np.int64)
        duration_set = df_duration['new']

        minimum = pd.to_timedelta(np.min(duration_set))
        maximum = pd.to_timedelta(np.max(duration_set))
        average = pd.to_timedelta(np.mean(duration_set))
        std = pd.to_timedelta(np.std(duration_set))
        variance = pd.to_timedelta(duration_set.var())
        coefficient_of_variance = std / average

        df = df.append({'Operation' : measurement, 'Min' : minimum, 'Max' : maximum, 'Mean' : average, 'Std': std, 'Var' : variance, 'CoV': coefficient_of_variance},
            ignore_index = True)

        sheet = file.split("/")[-1].replace(".xlsx", "")
        # Ricardo print(sheet)
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name=sheet, index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.close()