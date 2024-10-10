==========
Step
==========

search
-------------------

  The step search endpoint enables users to search for steps within the workflow. 
  This functionality provides a flexible way to find steps that match specific attributes, allowing users to identify tasks associated with a particular phase or stage in the production process.

.. http:post:: /zeafrost/api/v1/step/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/step/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific step. Use this parameter to retrieve details for a single step.
    :<json str step: Filter steps based on the unique identifier or name of a specific step.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``step`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``step``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.