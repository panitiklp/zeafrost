==========
Version
==========

search
-------------------

  The version search endpoint allows users to dynamically search for versions within the designated projects. 
  This functionality provides a flexible way to find versions that match specific attributes, including project associations, episode or shot identifiers, or other relevant criteria.

.. http:post:: /zeafrost/api/v1/version/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/version/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific version. Use this parameter to retrieve details for a single version.
    :<json str project: Filter versions based on the unique identifier or name of the project to which they belong.
    :<json str episode: Filter versions based on the unique identifier or name of the episode to which they belong.
    :<json str[] episodes:  An array of episode identifiers. Use this parameter to filter versions based on multiple episodes simultaneously.
    :<json str sequence: Filter versions based on the unique identifier or name of the sequence to which they belong.
    :<json str[] sequences: An array of sequence identifiers. Use this parameter to filter versions based on multiple sequences simultaneously.
    :<json str shot: Filter versions based on the unique identifier or name of the shot to which they belong.
    :<json str[] shots: An array of shot identifiers. Use this parameter to filter versions based on multiple shots simultaneously.
    :<json str asset_type: Filter versions based on the type or category of the associated asset.
    :<json str[] asset_types: An array of asset types. Use this parameter to filter versions based on multiple asset types simultaneously.
    :<json str asset: Filter versions based on the unique identifier or name of the associated asset.
    :<json str[] assets: An array of asset identifiers. Use this parameter to filter versions based on multiple assets simultaneously. 
    :<json str step: Filter versions based on the specific step or phase of the workflow.
    :<json str task: Filter versions based on the unique identifier or name of the associated task.
    :<json str path_to_movie: Filter versions based on the path to the movie file.
    :<json str path_to_frames: Filter versions based on the path to the frames files.  
    :<json str path_to_client: Filter versions based on the path to the client files.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``version`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``version``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.