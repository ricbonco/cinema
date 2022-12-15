import pandas as pd
from datetime import datetime
import numpy as np
import sys, os, shutil

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('Summary.xlsx', engine='xlsxwriter')

#if len(sys.argv) == 3:
directory = sys.argv[1] 
#N = int(sys.argv[2])
#N = 10
#else:
#    directory = os.getcwd()

files = os.listdir(directory)
files_to_process = [f'{directory}/{f}' for f in files if os.path.isfile(directory+'/'+f) and ".xlsx" in f] #Filtering only the files.
# Ricardo print(files_to_process)

for file in files_to_process:
    df = pd.DataFrame(columns = ['Operation', 'Min', 'Max', 'Mean', 'Std', 'Variance', 'CoV'])
    df_cpu_final = pd.DataFrame(columns = ['Operation', 'Min', 'Max', 'Mean', 'Std', 'Variance', 'CoV'])
    df_ram_final = pd.DataFrame(columns = ['Operation', 'Min', 'Max', 'Mean', 'Std', 'Variance', 'CoV'])
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
        cpu_list = []

        df_time_start_list = df_start['Time'].tolist()
        df_time_end_list = df_end['Time'].tolist()

        cpu_list = df_start['CPU'].tolist() + df_end['CPU'].tolist()

        ram_list = df_start['RAM'].tolist() + df_end['RAM'].tolist()

        # Ricardo print(f'len start {len(df_start_list)} len end {len(df_end_list)} ')

        for i in range(len(df_time_start_list)):
            time_list.append(pd.to_datetime(df_time_end_list[i]) - pd.to_datetime(df_time_start_list[i]))

        df_duration = pd.DataFrame (time_list, columns = ['Duration'])

        df_duration['new'] = df_duration['Duration'].values.astype(np.int64)
        duration_set = df_duration['new']

        duration_set_list = duration_set.tolist()
        duration_set_list.sort()

        #cpu_list.sort()

        N = int(round(len(duration_set_list) * 0.01, 0) / 2) 
        print (f'N: {N}')

        del duration_set_list[:N]
        del duration_set_list[-N:]

        #del cpu_list[:N]
        #del cpu_list[-N:]

        duration_set = pd.Series(duration_set_list)

        series_cpu = pd.Series(cpu_list)

        series_ram = pd.Series(ram_list)

        # Time
        minimum_time = pd.to_timedelta(np.min(duration_set))
        maximum_time = pd.to_timedelta(np.max(duration_set))
        average_time = pd.to_timedelta(np.mean(duration_set))
        std_time = pd.to_timedelta(np.std(duration_set))
        variance_time = duration_set.var(ddof=0)
        coefficient_of_variance_time = std_time / average_time

        df = df.append({'Operation' : measurement, 'Min' : minimum_time, 'Max' : maximum_time, 'Mean' : average_time, 'Std': std_time, 'Variance' : variance_time, 'CoV': coefficient_of_variance_time},
            ignore_index = True)

        # CPU Usage
        minimum_cpu = pd.to_numeric(np.min(series_cpu))
        maximum_cpu = pd.to_numeric(np.max(series_cpu))
        average_cpu = pd.to_numeric(np.mean(series_cpu))
        std_cpu = pd.to_numeric(np.std(series_cpu))
        variance_cpu = series_cpu.var(ddof=0)
        coefficient_of_variance_cpu = std_cpu / average_cpu

        df_cpu_final = df_cpu_final.append({'Operation' : measurement, 'Min' : minimum_cpu, 'Max' : maximum_cpu, 'Mean' : average_cpu, 'Std': std_cpu, 'Variance' : variance_cpu, 'CoV': coefficient_of_variance_cpu},
            ignore_index = True)

        # RAM Usage
        minimum_ram = pd.to_numeric(np.min(series_ram))
        maximum_ram = pd.to_numeric(np.max(series_ram))
        average_ram = pd.to_numeric(np.mean(series_ram))
        std_ram = pd.to_numeric(np.std(series_ram))
        variance_ram = series_ram.var(ddof=0)
        coefficient_of_variance_ram = std_ram / average_ram

        df_ram_final = df_ram_final.append({'Operation' : measurement, 'Min' : minimum_ram, 'Max' : maximum_ram, 'Mean' : average_ram, 'Std': std_ram, 'Variance' : variance_ram, 'CoV': coefficient_of_variance_ram},
            ignore_index = True)
            
        sheet_time = f'{file.split("/")[-1].replace(".xlsx", "")}_time'
        sheet_cpu = f'{file.split("/")[-1].replace(".xlsx", "")}_cpu'
        sheet_ram = f'{file.split("/")[-1].replace(".xlsx", "")}_ram'
        # Ricardo print(sheet)
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name=sheet_time, index=False)
        df_cpu_final.to_excel(writer, sheet_name=sheet_cpu, index=False)
        df_ram_final.to_excel(writer, sheet_name=sheet_ram, index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.close()

shutil.move('Summary.xlsx', f"{directory}/Summary.xlsx")