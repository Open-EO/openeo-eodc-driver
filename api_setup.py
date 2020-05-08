import os
import json
import requests


def get_headers(backend_url, username, password):
    # Get token with Basic auth
    response = requests.get(backend_url + "/credentials/basic", auth=(username, password))
    if "v0.4" in backend_url:
        headers = {'Authorization': 'Bearer ' + response.json()['token']}
    else:
        headers = {'Authorization': 'Bearer basic//' + response.json()['access_token']}

    return headers
    

def add_processes(backend_url, auth_header):
    
    # Load process list supported
    processes = json.load(open("supported_processes.json"))["processes"]
    processes_to_add = {process_name:{} for process_name in processes}
    
    if "v0.4" in backend_url:
        response = requests.post(backend_url + "/processes", json=processes_to_add, headers=auth_header)
        if response.ok:
            print('All processes added to back-end.')
            print(response.headers['Location'])
        else:
            print(response.text)
    else:    
        for process_name in processes:
            response = requests.put(backend_url + "/processes/" + process_name, headers=auth_header)
            if response.ok:
                print(f'Successfully added process {process_name} to back-end.')
            else:
                print(process_name)
                print(response.text)
                print('\n')

        
def add_collections(backend_url, auth_header):
    
    response = requests.post(backend_url + "/collections", headers=auth_header)
    print(response.text)


if __name__ == '__main__':
    
    # Get env variables
    backend_url = os.environ['BACKEND_URL']
    username = os.environ['USER_BASIC_ADMIN']  # user MUST have admin rights
    password = os.environ['PASSWORD_BASIC_ADMIN']
    
    # Generate auth headers
    auth_header = get_headers(backend_url, username, password)
    
    # Add processes
    add_processes(backend_url, auth_header)
    
    # Add collections
    add_collections(backend_url, auth_header)
