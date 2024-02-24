from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
import os

# Definimos el alcance de la aplicación
SCOPES = ['https://www.googleapis.com/auth/drive']

backup_folder_id = 'ID_De_Carpeta_Drive'

local_directory = 'dirección/de/fichero'

# Configuramos la autenticación de Drive
creds = None
if os.path.exists('credenciales.json'):
    creds = ServiceAccountCredentials.from_service_account_file('credenciales.json')
elif os.path.exists('archivoToken.json'):
    creds = Credentials.from_authorized_user_file('archivoToken.json')
    
# Construimos el servicio de Drive
service = build('drive', 'v3', credentials = creds)

#Listamos los archivos de la carpeta de respaldo
backup_files = service.files().list(q=f"'{backup_folder_id}' in parents and trashed = false", fields = 'files(id, name)').execute()
backup_files_dict = {file['name']: file['id'] for file in backup_files['files']}

# Logica para subir y actualizar archivos en Drive
for filename in os.listdir(local_directory):
    file_path = os.path.join(local_directory, filename)
    if os.path.isfile(file_path):
        file_metadata = {'name': filename}
        if filename in backup_files_dict:
            file_id = backup_files_dict[filename]
            media = MediaFileUpload(file_path, resumable = True)
            service.files().update(fileId = file_id, media_body = media).execute()
            print(f'Archivo actualizado en Drive: {filename}')
        else:
            media = MediaFileUpload(file_path, resumable = True)
            file_metadata['parents'] = [backup_folder_id]
            service.files().create(body = file_metadata, media_body = media).execute()
            print(f'Archivo subido a Drive: {filename}')
            
print('Proceso de respaldo completado')
