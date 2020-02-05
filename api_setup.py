import os
import json
import requests


def get_headers(backend_url, username, password):
    # Get token with Basic auth
    response = requests.get(backend_url + "/credentials/basic", auth=(username, password))
    headers = {'Authorization': 'Bearer ' + response.json()['token']}
    
    return headers
    

def add_processes(backend_url, auth_header):
    
    # Load process list supported
    processes = json.load(open("supported_processes.json"))["processes"]
    processes_to_add = {process_name:{} for process_name in processes}
    
    response = requests.post(backend_url + "/processes", json=processes_to_add, headers=auth_header)
    if response.ok:
        print(response.headers['Location'])
    else:
        print(response.text)

        
def add_collections(backend_url, auth_header):
    
    response = requests.post(backend_url + "/collections", headers=auth_header)


if __name__ == '__main__':
    
    # Get env variables
    backend_url = os.environ['BACKEND_URL']
    username = os.environ['USER_BASIC']  # user MUST have admin rights
    password = os.environ['PASSWORD_BASIC']
    
    # Generate auth headers
    auth_header = get_headers(backend_url, username, password)
    
    # Add processes
    add_processes(backend_url, auth_header)
    
    # Add collections
    add_collections(backend_url, auth_header)
