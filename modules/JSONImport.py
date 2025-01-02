import json
from datetime import datetime
import psycopg

"""

REMEMBER TO UPDATE THE TABLE YOUR ARE UPLOADING DATA TO


"""




# Database connection setup
conn = psycopg.connect(
    host="localhost",
    dbname="Quest Top Times",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()

json_file = r"C:\Users\cbush\OneDrive\Desktop\Python_Practice\swimStuff\Top10Reporting\DATA\Quest_LCM.json"

# Load JSON data
with open(json_file, "r") as file:
    data = json.load(file)
    records = data.get("Table2", {}).get("Detail_Collection", [])

    for record in records:
        try:
            # Ensure all values are strings
            formatted_record = {key: str(value) if value is not None else "" for key, value in record.items()}

            # Parse date for TextBox59 (ensure it's stored as a string if needed)
            try:
                if formatted_record["TextBox59"]:
                    formatted_record["TextBox59"] = datetime.strptime(
                        formatted_record["TextBox59"], "%m/%d/%Y"
                    ).strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD format
            except ValueError:
                formatted_record["TextBox59"] = ""  # Set empty if date is invalid

            # Insert the record
            cursor.execute(
                """
                INSERT INTO lcm_top_times (
                    memberid, Top_Time, Event_Code, Swim_Time, powerpoints,
                    First_Name, Last_Name, Age_As_Of_Date, Type_Code, Club_Code,
                    TextBox59, meetname, timestandardname, Age_Group_Desc
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    formatted_record.get("memberid", ""),
                    formatted_record.get("Top Time", ""),
                    formatted_record.get("Event Code", ""),
                    formatted_record.get("Swim Time", ""),
                    formatted_record.get("powerpoints", "0"),  # Default to "0" if missing
                    formatted_record.get("First Name", ""),
                    formatted_record.get("Last Name", ""),
                    formatted_record.get("Age As Of Date", ""),
                    formatted_record.get("Type Code", ""),
                    formatted_record.get("Club Code", ""),
                    formatted_record.get("TextBox59", ""),
                    formatted_record.get("meetname", ""),
                    formatted_record.get("timestandardname", ""),
                    formatted_record.get("Age Group Desc", "")
                )
            )
        except Exception as e:
            # Log the error and continue with the next record
            print(f"Error inserting record: {record}\nError: {e}")
            conn.rollback()  # Rollback transaction for the current record
        else:
            conn.commit()  # Commit transaction for successful insert

# Close the connection
cursor.close()
conn.close()
print("All records have been processed and inserted successfully.")
