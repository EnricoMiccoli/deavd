# Search bar queries

The user can pose advanced queries in the search bar using three features:

* implicit `and`
* `-` negation
* `a/b` construct (or)

## Implicit and
By default, when the user enters multiple tags (ie.: space-separated words) in the search bar the system returns the entities that are tagged with all the specified tags.

Example queries: `red square`, `green star`.

## Negation
Searching for `-tag` return all entities not tagged with `tag`. The tagname and the `-` must not be separated.

The terms cannot be separated by spaces.

Example queries: `-red`, `-circle`.

## Or construct
Searching for `a/b` return all the entities tagged with `a`, `b`, or both. The construct can have as many terms as the user needs, like this: `red/green/blue` or `circle/square/red/star`.

## Complex queries
All of the features can be combined, eg:

* `red circle/square`
* `green/blue -star`
