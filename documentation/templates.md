# Templates
Stored in `sitefiles/templates`. They are used to build the web pages. Refer to the `flask` and `Jinja2` docs for more details.

Below are listed all the available templates with their arguments. Args between parens are optional.

## base
> Defines basic document structure, doctype and imports main css. Also includes the footer.

*No arguments*

## bucketpage
> Lists all ents in a bucket.

* `bucket` Bucket object as defined in deavd.py
* `fbp` Father Bucket Path, the actual path of the bucket the ent belongs to. Since search results are returned as a bucket named 'Results of your query' `fbp` is necessary to properly identify the ent.
* (`empty`) boolean, true if the bucket is empty.

## entitypage
> Showcases an ent along with its tags.

* `ent` Entity object as defined in deavd.py
* `bucketname` name of the bucket the ent belongs to

## homepage
> Homepage of the website. Index of all available buckets.

* `buckets` list of the Bucket objects to be indexed.

## login
> Prompts for username and password. Makes a post request, if the credentials given are correct the server-side var `mastersession['authenticated']` is set to True. Should only be used for debugging: the user will automatically be prompted for authentication when needed.

*No arguments*

## message
> Versatile template to inform the user. Should only be used for short messages, no more than one paragraph. Can display a title, a body, and a link. Used also to build error pages that offer a link back to the homepage.

* (`title`) content of the h1
* (`message`) content of the p
* (`link`) array: `link[0]` is the href, `link[1]` the anchor text

## nobucketfound
> Error page returned when the user asks for a bucket absent on the server.

* `bucketname` name of the absent bucket

## noentityfound
> Error page returned when the user asks for an ent not present in the current bucket.

* `entityname` name of the absent ent
* `bucketname` name of the bucket the ent was searched in
