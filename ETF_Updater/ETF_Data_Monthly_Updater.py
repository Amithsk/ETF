#Code to update the ETF daily transaction details into the DB
#Code picksup the ETF's details from a single location,this location has the information from NSE and AMI websites
import pandas as pd
from datetime import datetime
import os

# Function to merge two CSV files based on the 'Date' column
def merge_csv_files(directory, output_file_path):

    # Get the list of all CSV files in the folder
    csv_files=[f for f in os.listdir(directory) if f.endswith('.csv')]

    #Check if there are exactly two CSV files
    if len(csv_files) != 2:
        raise ValueError("There must be exactly two CSV files in the directory")
    
    #Construct the file full paths
    nse_file_path =os.path.join(directory,csv_files[0])
    ami_file_path= os.path.join(directory,csv_files[1])

    #Load the CSV files
    nse_data=pd.read_csv(nse_file_path)
    ami_data=pd.read_csv(ami_file_path)

    #Merge the two datasets based on the 'Date' column
    merged_data = pd.merge(nse_data,ami_data,on='Date')

    #Get the current date in YYYY-MM-DD format
    current_date=datetime.now().strftime("%Y-%m-%d")

    #Append the current date to the output filename
    output_file_with_date=f"{output_file_path}_{current_date}.csv"
    output_file_path=os.path.join(output_file_path,output_file_with_date)


    # Save the merged dataset to the specified output file path
    merged_data.to_csv(output_file_path, index=False)

    return output_file_path

# Example usage
directory = input("Enter the path to the NSE/AMI CSV file: ")
output_file_path = input("Enter the path where the merged CSV file should be saved: ")

merged_file = merge_csv_files(directory, output_file_path)
print(f"Merged CSV file saved at: {merged_file}")
