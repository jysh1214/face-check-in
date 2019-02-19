import os

import face_recognition

# google api
from oauth2client.service_account import ServiceAccountCredentials as SAC

import gspread
import json
import sys

# Google Sheet Config
GDriveJSON = 
GSpreadSheet = 

# Google Sheet column value
ID = 1
NAME = 2
DIVISION = 3
DEPARTMENT = 4
MOBILEPHONE = 5
EMAIL = 6
ATTENDTIMES = 7


# Connect to Google Sheet
try:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/drive.readonly',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/spreadsheets.readonly']
    key = SAC.from_json_keyfile_name(GDriveJSON, scope)
    gc = gspread.authorize(key)
    worksheet = gc.open(GSpreadSheet).sheet1 # sheet1: member

except Exception as ex:
    print('無法連線Google Sheet', ex)
    sys.exit(1)

# Root directory of the project
IMAGE_DIR = os.path.abspath("./face_image")
file_names = next(os.walk(IMAGE_DIR))[2]

class Database:
    def __init__(self):
        # Create arrays of known face encodings and their names
        self.known_face_encodings = []
        self.known_face_names = []

        # Create arrays of data
        self.student_data_dict = {}

        # Load all pictures and learn how to recognize it.
        for i in range(len(file_names)):
            file_name = file_names[i]
            
            # jyx_image = face_recognition.load_image_file("IMAGE_DIR/107598061.png")
            # jyx_face_encoding = face_recognition.face_encodings(jyx_image)[0]

            face_image = face_recognition.load_image_file(os.path.join(IMAGE_DIR, file_name))
            face_encoding = face_recognition.face_encodings(face_image)[0]
            self.known_face_encodings.append(face_encoding)

            file_name = file_name.split('.', 2)[0] # remove ".png"
            self.known_face_names.append(file_name)

            # Loading data from google sheet
            try:
                label_list = worksheet.col_values(ID) # column A
                which_row = 0
                for label in label_list:
                    which_row += 1
                    if (label == file_name):
                        self.student_data_dict[file_name] = worksheet.row_values(which_row)
                        # self.student_data_list.append((, worksheet.row_values(which_row)))
                        # data_list = worksheet.row_values(which_row)
                        # print(data_list)
                        
            except Exception as ex:    
                print('無法使用Google Sheet: ', ex)
                sys.exit(1)

        print("目前已登錄名單：")
        for i in range(len(self.known_face_names)):
            print(self.known_face_names[i])

    def get_known_face_encodings(self):
        return self.known_face_encodings

    def get_known_face_names(self):
        return self.known_face_names

    def get_student_data_list(self, name):
        return self.student_data_dict[name]

    def check_in(self, name):
        try:
            label_list = worksheet.col_values(1) # column A
            which_row = 0
            for label in label_list:
                which_row += 1
                if (label == name):
                    times = int(worksheet.row_values(which_row)[ATTENDTIMES]) + 1
                    print(times)
                    worksheet.update_cell(which_row, ATTENDTIMES, str(times))

            return True

        except Exception as ex:    
            print('無法使用Google Sheet: ', ex)
            sys.exit(1)


'''Create an encoder subclassing JSON.encoder. 
Make this encoder aware of our classes (e.g. datetime.datetime objects) 
'''
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

def get_google_sheet(spreadsheet_id, range_name):
    gsheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return gsheet
