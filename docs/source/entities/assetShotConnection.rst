=====================
AssetShotConnection
=====================

search
-------------------

  The assetShotConnection search endpoint allows users to dynamically search for connections between assets and shots within the designated projects. 
  This functionality provides a flexible way to find connections that match specific attributes, including entity types, episode associations, sequence associations, and shot associations.

.. http:post:: /zeafrost/api/v1/assetshotconnection/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/assetshotconnection/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific asset-shot connection. Use this parameter to retrieve details for a single connection.
    :<json str entity: Filter connections based on the type of entity associated with the connection.
    :<json str episode: Filter connections based on the unique identifier or name of the episode to which they belong.
    :<json str sequence: Filter connections based on the unique identifier or name of the sequence to which they belong.
    :<json str shot: Filter connections based on the unique identifier or name of the shot to which they belong.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``assetShotConnection`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``assetShotConnection``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.