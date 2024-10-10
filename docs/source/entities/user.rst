==================
User
==================

search
------------

  The User Search endpoint allows users to dynamically search for users within the organization. 
  This functionality provides a flexible way to find users that match specific attributes, including the unique identifier or name of the user.

.. http:post:: /zeafrost/api/v1/user/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/user/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific user. Use this parameter to retrieve details for a single user.
    :<json str username: Filter users based on the unique username.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``user`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``user``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.

    .. note::

        The user endpoint allows users to search for users using flexible queries that may include the unique identifier or name of the user.