=============
Sequence
=============

search
-------------------

  The sequence search endpoint allows users to search for sequences within the projects. 
  This feature provides a flexible way to find sequences that match specific attributes, enabling efficient and targeted sequence retrieval.

.. http:post:: /zeafrost/api/v1/sequence/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/sequence/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id:   The unique identifier of a specific sequence. Use this parameter to retrieve details for a single sequence.
    :<json str project:  Filter sequence based on the unique identifier or name of the project to which they belong.
    :<json str episode:  Filter sequences based on the unique identifier or name of the episode to which they belong.
    :<json str[] episodes: An array of episode identifiers. Use this parameter to filter sequences based on multiple episodes simultaneously.
    :<json str sequence: Filter sequences based on the unique identifier or name of a specific sequence.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``sequence`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``sequence``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.