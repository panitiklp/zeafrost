=========================
Department
=========================

search
------------

  The department search endpoint allows users to dynamically search for departments within the organization. 
  This functionality provides a flexible way to find departments that match specific attributes, including the unique identifier or name of the department.

.. http:post:: /zeafrost/api/v1/department/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/department/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific department. Use this parameter to retrieve details for a single department.
    :<json str departrment: Filter departments based on the unique identifier or name of the department.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``department`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``department``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
