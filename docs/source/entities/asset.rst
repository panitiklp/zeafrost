=============
Asset
=============

search
-------------------

    The asset search endpoint allows users to find assets within the projects. 
    Users can filter assets based on attributes such as name, type, or project, facilitating targeted asset retrieval.

.. http:post:: /zeafrost/api/v1/asset/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/asset/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id:  The unique identifier of a specific asset. Use this parameter to retrieve details for a single asset.
    :<json int[] ids: An array of unique identifiers for multiple assets. Use this parameter to retrieve details for multiple assets simultaneously.
    :<json str project:   Filter assets based on the unique identifier or name of the project to which they belong.
    :<json str type:  Filter assets based on their type or category.
    :<json str[] types: An array of asset types. Use this parameter to filter assets based on multiple types simultaneously.
    :<json str asset_type: Filter assets based on their type or category, similar with ``type``
    :<json str[] asset_types: An array of asset types. Use this parameter to filter assets based on multiple types simultaneously, similar with ``types``
    :<json str asset: Filter assets based on the unique identifier or name of a specific asset.
    :<json str variation:  Filter assets based on a specific variation.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``asset`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``asset``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.