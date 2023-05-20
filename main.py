from bs4 import BeautifulSoup
import requests
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

url = "https://www.airbnb.com/s/Coeur-d'Alene--Idaho--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-06-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query=Coeur%20d%27Alene%2C%20ID&place_id=ChIJj3xVuvi0YVMRkFK_BVuZ5V8&date_picker_type=calendar&source=structured_search_input_header&search_type=autocomplete_click"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser', from_encoding="iso-8859-8")

target_class = 'g1qv1ctd cb4nyux dir dir-ltr'
head_class = "t1jojoys dir dir-ltr"

target_divs = soup.find_all('div', class_=target_class)

google_sheet_id = "1ThDgrginO0RlABE0_ef3k1LeJJ_rolknF_owD5AMrLs"

data_list = []
for div in target_divs:
    head = div.find("div", class_="t1jojoys dir dir-ltr").text
    desc = div.find_all("div", class_="f15liw5s s1cjsi4j dir dir-ltr")
    price_div = div.find("div", class_="pquyp1l dir dir-ltr")
    price_div2 = price_div.find("div")
    price_div3 = price_div2.find("div")
    price_span = price_div3.find("span")
    price_span_div = price_span.find("div")
    # price = price_span.find("span", class_="_1y74zjx")
    price = ""
    try:
        price = price_span.find("span", class_="_1y74zjx").text

    except:
        price = price_span.find("span", class_="_tyxjp1").text

    desc_arr = []
    for d in desc:
        text = d.text
        desc_arr.append(text)
    price = price.replace('\xa0', ' ')

    div_data = [head, price]
    div_data.extend(desc_arr)
    data_list.append(div_data)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def update_values(spreadsheet_id, range_name, value_input_option,
                  _values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:

        service = build('sheets', 'v4', credentials=creds)

        values = _values

        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


update_values(google_sheet_id,
              "A1:C1", "USER_ENTERED",
              [
                  ['Header', 'Price', 'Desc']

              ])
for i, data in enumerate(data_list):
    print(i, data)
    update_values(google_sheet_id,
                  "A" + str(i + 2) + ":F" + str(i + 2) + "", "USER_ENTERED",
                  [
                      data

                  ])
