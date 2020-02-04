import os
import json
import requests


def get_headers(backend_url, username, password):
    # Get token with Basic auth
    response = requests.get(backend_url + "/credentials/basic", auth=(username, password))
    aaa = response.json()
    aaa['token'] = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIyZWQwZGIxZjY2MWQ4OTg5OTY5YmFiNzhkMmZhZTc1NjRmZGMzYTkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI2MzEyMzU3MjExNjctczRibnIxanU0cG5vcjBoYzdzODJxOXFudWM2YjZuOGEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI2MzEyMzU3MjExNjctczRibnIxanU0cG5vcjBoYzdzODJxOXFudWM2YjZuOGEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDIxNDEzMjUzOTg2NjY3NzU0NzIiLCJlbWFpbCI6Imx1Y2EuZm9yZXN0YUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6ImtTdEVFbjVfcmNXTzZaOTg5ck8zX3ciLCJpYXQiOjE1ODA4MzM5NjcsImV4cCI6MTU4MDgzNzU2N30.G8zuzSuowO98_QLV5oTxK9WRfyeZcZ5x0HxewwcqWQibV3QGvGhSMW-B9z-2237U_XaizOa1xVw0ihnSdMA-yX7ZVGc3uimojVmzmib5W086Mmymn4WjZU-GCeOX0iSUop1Jpr4ONDYpuza3yg5W93sPpWa2NsThgmb3n5ZCmH5eGIIeeryHX3sBKtrYLI9lL5QoMvaf9PbzHxUZsMUl15kJhH6H5q3Jc3fv8ppBZJGGXS0xtxgNNlkk7Ixv54MXabBgsYSXF4x5RPssSt4rGvSY87LZFGF2h_TlZnLc-VDdOq9Pe2q-gI74GnRViGTPpyaejh79ltpzE3M1tCTa6Q"
    headers = {'Authorization': 'Bearer ' + aaa['token']}
    #headers = {'Authorization': 'Bearer ' + response.json()['token']}
    
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
    import pdb; pdb.set_trace()


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
