===========
Status
===========

search
------------

  The status search endpoint enables users to perform dynamic searches for statuses within the designated projects. 
  This functionality provides a flexible way to find statuses that match specific attributes, including the unique identifier or name of the status.

.. http:post:: /zeafrost/api/v1/status/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/status/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: he unique identifier of a specific status. Use this parameter to retrieve details for a single status.
    :<json str status: Filter statuses based on the unique identifier or name of the status.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``status`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``status``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
