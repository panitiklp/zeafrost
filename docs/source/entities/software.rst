==========
Software
==========

search
------------

  The software search endpoint allows users to dynamically search for software entries within the designated projects. 
  This functionality provides a flexible way to find software entries that match specific attributes, including the unique identifier or name of the software.

.. http:post:: /zeafrost/api/v1/software/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/software/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific software entry. Use this parameter to retrieve details for a single software entry.
    :<json str software: Filter software entries based on the unique identifier or name of the software.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``software`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``software``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
