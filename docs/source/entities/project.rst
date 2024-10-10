=============
Project
=============

search
-------------------

    The project search endpoint allows users to search for projects within the studio's ShotGrid instance, based on specified search criteria. 
    This functionality provides a flexible and efficient way to find projects that match specific attributes. 
    The response includes both ShotGrid data and local project configuration details.

.. http:post:: /zeafrost/api/v1/project/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/project/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id:  The unique identifier of the project.
    :<json str project:  The unique name of the project.
    :<json str type: Filter projects by type.
    :<json bool shotgrid:  If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    -----------------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``project`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``project``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
