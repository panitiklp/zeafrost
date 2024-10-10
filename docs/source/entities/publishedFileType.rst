=====================
PublishedFileType
=====================

search
-------------------

  The publishedFileType search endpoint empowers users to perform dynamic searches for file types within designated projects. 
  This feature provides a versatile way to find file types that match specific attributes, including type names or unique identifiers. 
  Users can utilize this functionality to identify supported file types associated with published files.

.. http:post:: /zeafrost/api/v1/publishedfiletype/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/publishedfiletype/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific published file type. Use this parameter to retrieve details for a single published file type.
    :<json str type: Filter published file types based on a specific type or category.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``publishedFileType`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``publishedFileType``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.