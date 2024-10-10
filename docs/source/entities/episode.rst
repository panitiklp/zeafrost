=============
Episode
=============

search
-------------------

  The episode search endpoint enables users to search for episodes within the projects. 
  This functionality provides a flexible way to find episodes that match specific attributes, facilitating quick and targeted episode retrieval.

.. http:post:: /zeafrost/api/v1/episode/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/episode/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id:   The unique identifier of a specific episode. Use this parameter to retrieve details for a single episode.
    :<json str project:  Filter episodes based on the unique identifier or name of the project to which they belong.
    :<json str episode: Filter episodes based on the unique identifier, name, or search string for a specific episode. This parameter serves as a flexible search query for episode attributes.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``episode`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``episode``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.