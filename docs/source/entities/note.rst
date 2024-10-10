==========
Note
==========

search
-------------------

  The note search endpoint allows users to dynamically search for notes within designated projects. 
  This feature provides flexibility in finding notes that match specific attributes, such as note content, unique identifiers, or associations with particular workflow steps or tasks.

.. http:post:: /zeafrost/api/v1/note/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/note/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific note. Use this parameter to retrieve details for a single note.
    :<json str step: Filter notes based on the specific step or phase of the workflow.
    :<json str task: Filter notes based on the unique identifier or name of the associated task.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``note`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``note``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.