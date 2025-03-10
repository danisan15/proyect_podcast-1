import json
from flask import Flask, request
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Load the JSON file containing the API key
with open('credentials.json') as f:
    credentials_json = json.load(f)

# Extract the API key from the JSON data
api_key = credentials_json['private_key']
print(api_key)

# load the Service Account credentials from a JSON file
credentials = service_account.Credentials.from_service_account_file(
    "credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)

# create a Google Sheets API client
service = build("sheets", "v4", credentials=credentials)

# define a Flask route that stores data in a Google Sheet


@app.route("/store_data", methods=["POST"])
def store_data():
    # specify the Google Sheet ID and range to write to
    sheet_id = "1_liLZifZfL7_mOkWW1dVGdQ-PmrEk4VuGiNYdW_xAEM"
    range_name = "Database!A2:C"

    # get the data from the request body as a JSON object
    data = request.get_json()

    # create a set of unique email addresses from the incoming request
    new_emails = set()
    rows = []
    for item in data:
        email = item["email"]
        if email not in new_emails:
            new_emails.add(email)
            rows.append([email, item["name"], item["created_at"]])

    sent_data = rows.copy()

    # call the Google Sheets API to get the existing data in the sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name,
    ).execute()

    # check for duplicate email addresses in the existing data and append new rows for unique email addresses
    existing_data = result.get("values", [])
    for row in existing_data:
        email = row[0]
        if email == sent_data[0][0]:
            return "No new data to store in Google Sheet"

    # find the last row in the sheet and append the new data to it
    write_result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": sent_data},
    ).execute()

    # return a response indicating success or failure
    if len(write_result["updates"]) > 0:
        return "Data stored in Google Sheet successfully"
    else:
        return "Failed to store data in Google Sheet"


@app.route('/check_user', methods=['POST'])
def check_user():
    # Get the JSON data from the request body
    data = request.get_json()

    # Extract the email and password from the JSON data
    for item in data:
        sent_email = item["email"]

    # Call the Google Sheets API to get the data for the specified email
    sheet_id = '1_liLZifZfL7_mOkWW1dVGdQ-PmrEk4VuGiNYdW_xAEM'
    range_name = 'Database!A2:C'
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name,
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING',
        majorDimension='ROWS',
    ).execute()

    # Check if the email exists in the sheet
    existing_data = result.get('values', [])
    if len(existing_data) == 0:
        return 'Email not found', 404

    # Check if the email is correct
    is_found = False
    for item in existing_data:
        email = item[0]
        if email == sent_email:
            is_found = True
    if is_found is True:
        return str(is_found)
    else:
        return str(is_found), 404


if __name__ == "__main__":
    # start the Flask application
    app.run(debug=True)
