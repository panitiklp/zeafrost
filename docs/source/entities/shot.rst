=============
Shot
=============

search
-------------------

  The shot search endpoint facilitates dynamic searches for shots within specified projects. 
  This feature allows users to locate shots based on various attributes, including name, unique identifier, or other relevant criteria.

.. http:post:: /zeafrost/api/v1/shot/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/shot/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific shot. Use this parameter to retrieve details for a single shot.
    :<json int[] ids: An array of unique identifiers for multiple shots. Use this parameter to retrieve details for multiple shots simultaneously.
    :<json str project: Filter shots based on the unique identifier or name of the project to which they belong.
    :<json str episode: Filter shots based on the unique identifier or name of the episode to which they belong. 
    :<json str sequence:  Filter shots based on the unique identifier or name of the sequence to which they belong.
    :<json str[] sequences:  An array of sequence identifiers. Use this parameter to filter shots based on multiple sequences simultaneously.
    :<json str shot: Filter shots based on the unique identifier or name of a specific shot.
    :<json str[] shots: An array of shot identifiers. Use this parameter to filter shots based on multiple shots simultaneously.
    :<json str longname: Filter shots based on a long name.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``shot`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``shot``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.