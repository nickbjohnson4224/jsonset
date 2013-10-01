jsonset is a way of expressing an abstract set of JSON documents, much like
JSON Schema. However, JSON Schema is complex, implemented inconsistently,
and is clearly designed for specifying more "document-like" validations.
That's not necessarily bad, and at least it is close to being a standard, 
but it does not fit my requirements at the moment.

Some examples for before I document things properly:
====================================================

A document almost always matches itself
---------------------------------------

{"a":["b","c",4]} in jsonset.loads('{"a":["b","c",4]}') == True

$ is used to denote special directives
--------------------------------------

"a" in jsonset.loads('{"$union":["a", "b", "c"]}') == True

Here are some directives:
-------------------------

{ "$union" : [ "$string", 42 ] }
{ "$and" : [ "$string", { "$length" : 5 } ] }
{ "$array" : "$number" }
{ "$range" : [ 5, null ] }
{ "foo" : "$boolean" }

"$$foo" evaluates to the literal "$foo" (escapes for $ past the first one are unnecessary)
