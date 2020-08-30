# Exercise-restapi-flask
* missing unittest

## Install all requirements:
* pip install -r requirements.txt

## Run local server:
* python app.py

## Endpoints
 * /api/v1/file_system/list
 * /api/v1/file_system/info
 * /api/v1/file_system/create
 * /api/v1/file_system/delete
 
- use only POST method
- data has contain path argument '{"path":"/example.txt"}'


## Example with curl 
* curl --header "Content-Type: application/json" --request POST --data '{"path":"/"}' http://127.0.0.1:5000/api/v1/file_system/list
* curl --header "Content-Type: application/json" --request POST --data '{"path":"/example.txt"}' http://127.0.0.1:5000/api/v1/file_system/info
* curl --header "Content-Type: application/json" --request POST --data '{"path":"/subfolder/example.txt"}' http://127.0.0.1:5000/api/v1/file_system/create
* curl --header "Content-Type: application/json" --request POST --data '{"path":"/subfolder/example.txt"}' http://127.0.0.1:5000/api/v1/file_system/delete
