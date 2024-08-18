import folium
import os
import time
import json
import re
import argparse
import pandas as pd
from selenium import webdriver

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


def collect_images(folder_id, service, data_file, saved_locs):
    columns = ['Country', 'Break', 'Lat', 'Long']
    df = pd.read_csv(data_file, usecols=columns)
    # temp_df = df[df['Saved'] == 'N']
    # start_idx = temp_df.index[0]
    # df = df[:10]

    delay=5
    fn='temp_map.html'
    path = path=os.getcwd()

    # try:
    for idx, row in df.iterrows():
        lat, long = row.Lat, row.Long

        if row.Break in saved_locs:
            continue

        m = folium.Map(location=[lat,long], zoom_start=16)
        tile = folium.TileLayer(
                tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr = 'Esri',
                name = 'Esri Satellite',
                overlay = False,
                control = True
            ).add_to(m)
        
        #Save the map as an HTML file
        tmpurl=f'file://{path}/{fn}'
        m.save(fn)
        browser = webdriver.Chrome()
        browser.get(tmpurl)    
        time.sleep(delay)
        map_file = f'{row.Country}_{row.Break}.png'
        browser.save_screenshot(map_file)
        browser.quit()

        try:
            file_metadata = {"name": map_file, 'parents': [folder_id]}
            media = MediaFileUpload(map_file, mimetype="image/png")
            # pylint: disable=maybe-no-member
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

        except HttpError as error:
            print(f"A file error occurred: {error}")
            file = None
        finally:
            os.remove(map_file)

    # except Exception as E:
    #     print(f"A file error occurred: {E}")
    #     file = None
    # finally:
    #     os.remove(map_file)
    #     df.Saved.iloc[start_idx:start_idx+idx] = 'Y'
    #     df.to_csv(data_file, index=False)

    os.remove(fn)


def create_folder(service, email, folder_name):
    try:
        # create drive api client
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(
            body=folder_metadata,
        ).execute()

        domain_permission = {
            'type': 'user',
            'emailAddress': email,
            'role': 'writer',
        }
        service.permissions().create(
            fileId=folder['id'],
            body=domain_permission,
        ).execute()

        folder_id = folder['id']

    except HttpError as error:
        print(f"A folder error occurred: {error}")
        folder_id = None

    return folder_id, service


def check_folder(service, folder_name):
    response = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()

    try:
        return response['files'][0]['id']
    except:
        return None


def list_items(service):
    results = (
        service.files()
        .list(pageSize=1000, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    # if not items:
    #     print("No files found.")
    # print("Files:")
    # for item in items:
    #     print(f"{item['name']} ({item['id']})")

    # return items


def main():

    # parser = argparse.ArgumentParser(description='Input JSON file with required credentials')
    # parser.add_argument('filename', help='name of credentials file')
    # args = parser.parse_args()

    # config_file = vars(args)['filename']
    config_file = './utils/config.json'

    with open(config_file, 'r') as f:
        cred_config = json.load(f)

    cred_file = cred_config['cred_file']
    email = cred_config['email']
    folder_name = cred_config['folder_name']
    data_file = cred_config['data_file']
    delete = cred_config['delete']

    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = cred_file

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("drive", "v3", credentials=creds)

    # check if the given folder name exists and delete the folder if the user wants to clear it        
    folder_id = check_folder(service, folder_name)
    if folder_id and delete:
        try:
            service.files().delete(fileId=folder_id).execute()
            print(f"Successfully deleted file/folder with ID: {folder_id}")
            time.sleep(2)
        except Exception as e:
            print(f"Error deleting file/folder with ID: {folder_id}")
            print(f"Error details: {str(e)}")  

    # create the folder if it doesn't exist or if it was deleted
    if not folder_id or delete:
        folder_id, service = create_folder(service, email, folder_name)


    # collect existing file names to know which files not to scrape again
    results = (
        service.files()
        .list(pageSize=1000, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])
    saved_locs = set()

    for item in items:
        loc_match = re.search('\w+?_(\w+)\.png', item['name'])
        if loc_match:
            loc_name = loc_match.group(1)
            saved_locs.add(loc_name)


    # begin scraping image files
    collect_images(folder_id, service, data_file, saved_locs)



if __name__ == '__main__':
    main()
