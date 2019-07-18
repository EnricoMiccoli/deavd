# DEAVD
### Deductive Entity Attribute Value Database
Deavd is a tag based database that can be used as the backend for an archiving application.
It's written in python3 and uses Flask as a webserver.

## [Live Demo](https://7f4652bb655.pythonanywhere.com/b/shapes/0)
Play around with a working example [here](https://7f4652bb655.pythonanywhere.com/b/shapes/0).

See [querying](documentation/querying.md) to learn more about searching.

## Dependencies
* Flask
* Flask-Scss
* flask-compress
* PyYaml
* bcrypt

## Running
`$ python webserver.py`

If you are running this app on a network you should set `debug: False` in `config.yaml`.

More information is provided in the [documentation](documentation) folder.
