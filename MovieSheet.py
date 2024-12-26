import gspread # high level api on top of low level google sheets api operations
from google.oauth2.service_account import Credentials
import requests
import re


class MovieSheet:
    def __init__(self):
        # what we want to access
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        # authorize using the credentials.json file
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_id = "1KB3zdLDbbATAKKwgOOmPXEdDqDubNlVQjuVcyykxhsA"
        sheet = client.open_by_key(sheet_id) # the whole sheet
        
        self.worksheet = sheet.worksheet("Jest oglądane") # worksheet with movies "Jest oglądane"
        self.used_rows = len(self.worksheet.get_all_values())
        self.used_cols = len(self.worksheet.get_all_values()[0])

    def _parse_omdb_response(self, imdb_id: str) -> dict:
        payload: dict = {
            "apikey": "35cd64fc",
            "i": imdb_id
        }
        
        r: requests.Response = requests.get("http://www.omdbapi.com", params=payload)
        r_dict = r.json()
        
        parsed_dict = {
            "Title": r_dict["Title"],
            "Year": r_dict["Year"],
            "Runtime": r_dict["Runtime"],
        }
        
        return parsed_dict
    
    def _parse_imdb_link(self, imdb_link: str) -> str:
        if match := re.fullmatch(r"https://www\.imdb\.com/title/(tt.+)/.*", imdb_link):
            return match.group(1)
        raise ValueError("Couldn't parse imdb_link. Are you sure it's correct?")
    
    def update_row(self, row_id: int) -> None:
        if self.worksheet.cell(row_id, 3).value is not None: # TODO: check for every value, not just "rok"
            return
        
        imdb_id: str = self._parse_imdb_link(self.worksheet.cell(row_id, 1).value)
        values_to_insert: dict = self._parse_omdb_response(imdb_id)
        
        self.worksheet.update_cell(row_id, 2, values_to_insert["Title"])
        self.worksheet.update_cell(row_id, 3, values_to_insert["Year"])
        self.worksheet.update_cell(row_id, 4, values_to_insert["Runtime"])
        print(f"Updated row {row_id}")
        