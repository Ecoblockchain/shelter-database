Web Services
============

Example of requests to the Web Service
--------------------------------------

.. code-block:: shell

    # Get the list of root categories
    $ GET http://127.0.0.1:5000/api/category?q={"filters":[{"name":"parent_id","op":"is_null"}]}
    # Get the list of child categories
    $ GET http://127.0.0.1:5000/api/category?q={"filters":[{"name":"parent_id","op":"is_not_null"}]}
    # Get information about the child category "Walls & Frame"
    $ GET http://127.0.0.1:5000/api/category?q={"filters":[{"name":"parent_id","op":"is_not_null"},{"name":"name","op":"eq","val":"Walls %26 frame"}]}

    # Get information about an attribute
    $ GET http://127.0.0.1:5000/api/attribute?q={"filters":[{"name":"name","op":"eq","val":"Landform"}]}
    $ GET http://127.0.0.1:5000/api/attribute?q={"filters":[{"name":"name","op":"eq","val":"Main hazards in country"}]}

    # Get the translations of a string
    $ GET http://127.0.0.1:5000/api/translation?q={"filters":[{"name":"original","op":"eq","val":"Name of shelter"}]}
