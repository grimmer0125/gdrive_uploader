# https://developers.google.com/drive/v3/web/quickstart/python

# service account, py:
# https://developers.google.com/api-client-library/python/auth/service-accounts
# https://github.com/google/google-api-python-client

# pip install --upgrade google-api-python-client
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery
from apiclient.http import MediaFileUpload
from apiclient import errors


# scopes = ['https://www.googleapis.com/auth/sqlservice.admin']
SCOPE1 = 'https://www.googleapis.com/auth/drive'  # drive.metadata.readonly
SCOPE2 = "https://www.googleapis.com/auth/drive.file"
SCOPE3 = "https://www.googleapis.com/auth/drive.metadata"

# ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.metadata"],

def get_credentials():
    scopes = [SCOPE1, SCOPE2, SCOPE3]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'gdrive.json', scopes)
    return credentials
    # http_auth = credentials.authorize(Http())

# only work for v2
def about(service):
    """Print information about the user along with the Drive API settings.

    Args:
      service: Drive API service instance.
    """
    try:
        about = service.about().get().execute()

        print('Current user name:{}'.format(about['name']))
        print('Root folder ID:{}'.format(about['rootFolderId']))
        print('Total quota (bytes):{}'.format(about['quotaBytesTotal']))
        print('Used quota (bytes):{}'.format(about['quotaBytesUsed']))
    except errors.HttpError as error:
        print('An error occurred:{}'.format(error))

# Current user name:travisci@clear-variety-168514.iam.gserviceaccount.com
# Root folder ID:0AGb4yMmbQLfsUk9PVA
# Total quota (bytes):16106127360
# Used quota (bytes): 16105814993
#                     10461753934


# TODO:
# Final two ways:
# 1. [no service account] use oauth and create credentials first, then save it as a credentials.txt
#  then script can use it to upload https://stackoverflow.com/questions/28208849/google-apps-managed-unlimited-account-storage-quota-for-service-account/28209753#28209753
# 2. GSuite domain admin setup DwD (domain-wide-delegation) forr service account,
#  https://stackoverflow.com/questions/40535355/how-to-fix-the-storage-exceeded-issue-for-google-drive-when-uploading-using-serv

# An error occurred: <HttpError 403 when requesting
# https://www.googleapis.com/drive/v2/files/1Or0Cg5dHFLyqaMKOAvfqxqWr8QlziP1R/permissions/16408764324948793154?alt=json
# returned "Insufficient permissions for this file">
# seems v2
def transfer_patch(service, file_id, permission_id, new_role):
  """Patch a permission's role.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to update permission for.
    permission_id: ID of the permission to patch.
    new_role: The value 'owner', 'writer' or 'reader'.

  Returns:
    The patched permission if successful, None otherwise.
  """
  patched_permission = {'role': new_role}
  try:
    return service.permissions().patch(
        fileId=file_id, permissionId=permission_id,
        body=patched_permission).execute()
  except errors.HttpError as error:
    print('An error occurred: {}'.format(error))
  return None

# seems v3
# https://developers.google.com/drive/v3/web/manage-sharing#transferring_ownership
# or use patch to transfer? https://developers.google.com/drive/v2/reference/permissions/patch
def transfer(service, file_id, target_email):
    # file_id = '1sTWaJ_j7PkjzaBWtNc3IzovK5hQf21FbOw9yLeeLPNQ'
    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            print("Permission Id: {}".format(response.get('id')))

    batch = service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'owner',
        'emailAddress': target_email
    }
    batch.add(service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
            transferOwnership=True
    ))
    # <HttpError 400 when requesting https://www.googleapis.com/drive/v3/files/1Or0Cg5dHFLyqaMKOAvfqxqWr8QlziP1R/permissions?fields=id&transferOwnership=true&alt=json
    # returned "Bad Request. User message: "You can't yet change the owner of this item. (We're working on it.)"">

    # domain_permission = {
    #     'type': 'domain',
    #     'role': 'reader',
    #     'domain': 'example.com'
    # }
    # batch.add(drive_service.permissions().create(
    #         fileId=file_id,
    #         body=domain_permission,
    #         fields='id',
    # ))
    batch.execute()

# only v2
def print_files_in_folder(service, folder_id):
    """Print files belonging to a folder.

    Args:
      service: Drive API service instance.
      folder_id: ID of the folder to print files from.
    """
    files = []
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.children().list(
                folderId=folder_id, **param).execute()

            for child in children.get('items', []):
                print('File Id:{}'.format(child['id']))
                files.append(child['id'])
            page_token = children.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred:{}'.format(error))
            break
    return files

# v3?
def delete_file(service, file_id):
    """Permanently delete a file, skipping the trash.

    Args:
      service: Drive API service instance.
      file_id: ID of the file to delete.
    """
    try:
        print("start to delete:{}".format(file_id))
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError as error:
        # if this file is owned by others, an exception will happen
        print('An error occurred:{}'.format(error))

# only v3, pageSize
def list(service):
        # example: List files
    results = service.files().list(
        pageSize=50, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
            # delete_file(service, item['id'])

# v2 uses insert but v3 uses create
def write():
    # write a file
    # ref: https://stackoverflow.com/questions/21415467/copy-file-into-a-specific-parent-folder-with-google-drive-api
    # target
    parentFolderId = "0B6SSpI8M8o7uRUtwV1Z3MGwtVGM"
    file_metadata = {
        'name': 'test7.png',
        'parents': [parentFolderId]
    }
    # source
    media = MediaFileUpload('test6.png',
                            mimetype='image/png',
                            resumable=True)
    # TODO
    # chunk upload: https://developers.google.com/api-client-library/python/guide/media_upload
    request = service.files().create(body=file_metadata,
                                     media_body=media,
                                     fields='id')

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded{}".format(int(status.progress() * 100)))
    print("Upload Complete!")

    # print('File ID:{}'.format(file.get('id')))


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(Http())
    service = discovery.build('drive', 'v2', http=http)

    #file = "1Or0Cg5dHFLyqaMKOAvfqxqWr8QlziP1R"
    # transfer(service, file, 'acdc_soft@asiaa.sinica.edu.tw')

    # permissions = service.permissions().list(fileId=file).execute()
    # transfer_patch(service, file, permissions['items'][1]['id'],"owner")

    # about(service)
    # list(service)
    # files = print_files_in_folder(service, "0B6SSpI8M8o7uRUtwV1Z3MGwtVGM")
    test_file = "1nLl_MAiobwbUtDEwKrfYXj1fuSwcgyMG"
    delete_file(service, test_file)
    # for file in files:
    #     transfer(service, file, 'acdc_soft@asiaa.sinica.edu.tw')
        # permissions = file1.auth.service.permissions().list(fileId=file1['id']).execute()
        # myperm_id = permissions['items'][1]['id'] # this is the second permission, i.e. of my main account
        # myperm = file1.auth.service.permissions().get(fileId=file1['id'], permissionId=myperm_id).execute()
        # permissionId=myperm['id']

        # delete_file(service, file)
        # param_perm = {}
        # param_perm['value'] = 'acdc_soft@asiaa.sinica.edu.tw'
        # param_perm['type'] = 'user'
        # param_perm['role'] = 'owner'
        # service.permissions().update(fileId=file,
        #                              # permissionId=perm_id,
        #                              body=param_perm,
        #                              transferOwnership=True).execute()

    return


if __name__ == '__main__':
    main()
