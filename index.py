# https://developers.google.com/drive/v3/web/quickstart/python

# service account, py:
# https://developers.google.com/api-client-library/python/auth/service-accounts
# https://github.com/google/google-api-python-client

# pip install --upgrade google-api-python-client
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery
from apiclient.http import MediaFileUpload

# scopes = ['https://www.googleapis.com/auth/sqlservice.admin']
SCOPE = 'https://www.googleapis.com/auth/drive' #drive.metadata.readonly

  # ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.metadata"],

def get_credentials():
    scopes = [SCOPE]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'gdrive.json', scopes)
    return credentials
# http_auth = credentials.authorize(Http())

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(Http())
    service = discovery.build('drive', 'v3', http=http)

    # write a file
    # ref: https://stackoverflow.com/questions/21415467/copy-file-into-a-specific-parent-folder-with-google-drive-api
    # target
    parentFolderId = "0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"
    file_metadata = {
      'name' : 'test7.png',
      'mimeType' : 'image/png',
      'parents' : [ { "id" : parentFolderId } ]
    }
    # source
    media = MediaFileUpload('test6.png',
                            mimetype='image/png',
                            resumable=True)
    # TODO
    # chunk upload: https://developers.google.com/api-client-library/python/guide/media_upload
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID:{}'.format(file.get('id')))

    # example: List files
    # results = service.files().list(
    #     pageSize=10,fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print('{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()
