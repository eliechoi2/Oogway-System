#Import appropriate libraries
import numpy as np
import pandas as pd
import os
from numpy import nan as NA
from datetime import datetime
from app import app, db 
from models import ShelfReading, Student

#New file path folder
excel_file_path = 'files.xlsx'

folder_name = os.path.splitext(os.path.basename(excel_file_path))[0]
parent_directory = "floor_3_collections" 

folder_path = os.path.join(parent_directory, folder_name)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    
    
    
#Read excel file of shelfreading data
all_sheets = pd.read_excel('Oogway-System\excel files\Copy of 3rd Floor SR.xlsx', sheet_name=None)


#Save each sheet as a separate CSV file
for sheet_name, df in all_sheets.items():
    file_path = os.path.join(folder_path, f"{sheet_name}.csv")
    df.to_csv(file_path, index=False)

print(f"All sheets saved as CSV files in the folder: {folder_path}")


student_listing = pd.read_csv('Oogway-System\excel files\Active CMR Student List - Sheet1.csv', header=None)
student_listing[['Last Name', 'First Name']] = student_listing[0].str.split(',', expand=True)
student_listing['First Name'] = student_listing['First Name'].str.strip()
student_listing['Last Name'] = student_listing['Last Name'].str.strip()
new_student_listing = student_listing.drop(columns=[0])


folder_name = os.path.splitext(os.path.basename(excel_file_path))[0] + "_edited"
parent_directory = "new_floor_3" 
folder_path = os.path.join(parent_directory, folder_name)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    
    
def edit_sheet(df, new_student_listing):
    default_datetime = pd.to_datetime('1900-01-01 00:00:00')
    default_time = default_datetime.time()
    default_date = pd.to_datetime('1900-01-01').date()
    # Select relevant columns from the input dataframe
    temp_df = df.iloc[:, [0, 1, 2, 3, 5, 6, 7]]
    temp_df.columns = ['Name', 'Date', 'Start Time', 'End Time', 'Shelves', 'Start Call #', 'Stop Call #']
    
    # Remove rows with all NaN values and reset index
    cleaned_temp_df = temp_df.dropna(how='all').drop(1).reset_index(drop=True)
    
    # Convert 'Start Time' and 'End Time' columns to datetime objects, assuming the format is 'HH:MM:SS'
    cleaned_temp_df['Start Time'] = pd.to_datetime(cleaned_temp_df['Start Time'], format='%H:%M:%S', errors='coerce')
    cleaned_temp_df['End Time'] = pd.to_datetime(cleaned_temp_df['End Time'], format='%H:%M:%S', errors='coerce')
    
    # Calculate 'Duration' as the difference between 'End Time' and 'Start Time'
    cleaned_temp_df['Duration'] = cleaned_temp_df.apply(
        lambda row: "error" if pd.isna(row['Start Time']) or pd.isna(row['End Time']) 
        else (row['End Time'] - row['Start Time']),
        axis=1
    )
    
    # If 'Duration' is a valid timedelta, convert it to hours, otherwise keep as "error"
    cleaned_temp_df['Duration'] = cleaned_temp_df['Duration'].apply(
        lambda x: round(x.total_seconds() / 3600, 2) if isinstance(x, pd.Timedelta) else "Error, missing value"
    )
    
    # Convert 'Start Time' and 'End Time' back to time format (without the date)
    cleaned_temp_df['Start Time'] = cleaned_temp_df['Start Time'].dt.strftime('%H:%M:%S')
    cleaned_temp_df['End Time'] = cleaned_temp_df['End Time'].dt.strftime('%H:%M:%S')
    
    # Merge cleaned_temp_df with new_student_listing to get the 'First Name' and 'Last Name'
    merged_df = cleaned_temp_df.merge(new_student_listing[['First Name', 'Last Name']], 
                                      left_on='Name', right_on='First Name', how='left')
    
    # For rows where 'Last Name' is NaN, populate 'First Name' from 'Name' and 'Last Name' as 'Missing'
    merged_df['First Name'] = merged_df['First Name'].fillna(merged_df['Name'])
    merged_df['Last Name'] = merged_df['Last Name'].fillna('Missing')
    
    # Drop the original 'Name' and 'First Name' columns
    merged_df = merged_df.drop(columns=['Name'])
    
    merged_df['Date'] = pd.to_datetime(merged_df['Date'], errors='coerce').dt.date
    merged_df['Start Time'] = merged_df['Start Time'].fillna(default_time)
    merged_df['End Time'] = merged_df['End Time'].fillna(default_time)
    merged_df['Date'] = merged_df['Date'].fillna(default_date)
    
    merged_df = merged_df.fillna("Missing")
    
    
    # Reorder columns to have 'First Name' and 'Last Name' at the beginning
    merged_df = merged_df[['First Name', 'Last Name', 'Date', 'Start Time', 'End Time', 
                           'Shelves', 'Start Call #', 'Stop Call #', 'Duration']]
    
    merged_df = merged_df[~((merged_df['Date'] == 'Missing') | 
                        (merged_df['Start Time'] == 'Missing') | 
                        (merged_df['End Time'] == 'Missing') | 
                        (merged_df['Last Name'] == 'Missing'))]

    # merged_df = merged_df[merged_df.apply(lambda row: row.isin(['Missing']).sum(), axis=1) < 4]
    
    return merged_df


for sheet_name, df in all_sheets.items():
    new_df = edit_sheet(df, new_student_listing)
    file_path = os.path.join(folder_path, f"{sheet_name}_edited.csv")
    new_df.to_csv(file_path, index=False)
    
    print(f"Edited sheet '{sheet_name}' saved to: {file_path}")

def get_student_id(first_name, last_name):
    student = Student.query.filter_by(student_fname=first_name, student_lname=last_name).first()
    if student is None:
        print(f"Warning: Student with name {first_name} {last_name} not found!")
        return None
    return student.student_id  # Access the correct attribute


def drop_specific_table():
    # Drop a specific table
    ShelfReading.__table__.drop(db.engine)
    print("Table dropped!")
    
# Insert CSV data into the database
from sqlalchemy.orm.exc import NoResultFound

def insert_data_to_db(csv_file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    for _, row in df.iterrows():
        # Get the student ID using the first and last name
        student_id = get_student_id(row['First Name'], row['Last Name'])
        
        # Check if the record already exists
        existing_record = ShelfReading.query.filter_by(
            date=row['date'],
            start_time=row['start_time'],
            student_id=student_id
        ).first()
        
        if existing_record is None:
            # If the record doesn't exist, insert it
            new_record = ShelfReading(
                date=row['date'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                shelves_completed=row['shelves_completed'],
                start_call=row['start_call'],
                end_call=row['end_call'],
                student_id=student_id,
                floor_id=row['floor_id']
            )
            db.session.add(new_record)
            db.session.commit()
        else:
            # Handle the case when the record already exists (optional)
            print(f"Duplicate found for student {student_id} on {row['date']} at {row['start_time']}")

if __name__ == '__main__':
    with app.app_context():  # This ensures you're within the application context
        csv_file_path = 'path/to/your/file.csv'
        insert_data_to_db(csv_file_path)
        
        
# Example usage for each edited CSV file
for sheet_name, df in all_sheets.items():
    csv_file_path = os.path.join(folder_path, f"{sheet_name}_edited.csv")
    insert_data_to_db(csv_file_path)
    
    
