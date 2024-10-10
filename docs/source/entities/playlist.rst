==========
Playlist
==========

search
------------


  The playlist search endpoint enables users to perform dynamic searches for playlists within the designated projects. 
  This functionality provides a flexible way to find playlists that match specific attributes, including project associations, workflow steps, or the unique identifier or name of the playlist.

.. http:post:: /zeafrost/api/v1/task/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/task/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific playlist. Use this parameter to retrieve details for a single playlist.
    :<json str project: Filter playlists based on the unique identifier or name of the project to which they belong. 
    :<json str step: Filter playlists based on the specific step or phase of the workflow.
    :<json str playlist: Filter playlists based on the unique identifier or name of the playlist.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``playlist`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``playlist``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
