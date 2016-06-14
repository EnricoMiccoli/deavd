# Directory structure
Everything besides `documentation/` is necessary to deploy the app.

* `documentation/` docs for the project
* `modules` extensions and modules imported by `webserver.py`
* `sitefiles`
    * `buckets` buckets to be served
    * `scss` scss files and partials
    * `static` contains the compiled css
        * `blobs` the actual stored files
    * `templates/` Jinja2 templates. Refer to [`documentation/templates.md`](templates.md) for details 
