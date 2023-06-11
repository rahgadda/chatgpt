import pandas as pd

# Replace 'file_path.xlsx' with the actual path of your Excel file
file_path = '/home/opc/dev/demo/ofsll_open_interface_manual_servicing.xlsx'

# Read all tabs from the Excel file into a dictionary of dataframes
dfs = pd.read_excel(file_path, sheet_name=None)

# Create an empty dictionary to store the combined values
combined_values = {}

# Loop through each dataframe in the dictionary
for sheet_name, df in dfs.items():
    # Get the column names and hints from the dataframe
    column_names = df['Column Name'].tolist()
    hints = df['Hint'].tolist()

    # Combine the values and add them to the dictionary
    combined_values.update({f"{sheet_name}.{column_names}": f"{column_names} {hint}" for column_names, hint in zip(column_names, hints)})

# Print the combined values
for key, value in combined_values.items():
    
    print(f"Key: {key}")
    print(f"Value: {value}")
    print("-------------------------")

