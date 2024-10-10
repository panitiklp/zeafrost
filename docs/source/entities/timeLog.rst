=========================
TimeLog
=========================

search
------------

  The timelog search endpoint allows users to dynamically search for timelog entries within the designated tasks. 
  This functionality provides a flexible way to find timelog entries that match specific attributes, including the unique identifier or name of the associated task.

.. http:post:: /zeafrost/api/v1/timelog/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/timelog/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific timelog entry. Use this parameter to retrieve details for a single timelog entry.
    :<json int task_id: Filter timelog entries based on the unique identifier or name of the associated task.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``timeLog`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``timeLog``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
