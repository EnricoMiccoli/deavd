# DEAVD
### Deductive Entity Attribute Value Database
Deavd is a tag based database that can be used as the backend for an archiving application.
It's written in python3 and uses Flask as a webserver.

## Dependencies
* Flask
* Flask-Scss
* PyYaml
* bcrypt

## Running
`$ python webserver.py`

If you are running this app on a network you should set `debug: False` in `config.yaml`.
