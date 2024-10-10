===============
PublishedFile
===============

search
-------------------

  The publishedFile search endpoint empowers users to perform dynamic searches for published files within the designated projects. 
  This feature provides a versatile way to find published files that match specific attributes, including codes, entity types, project associations, workflow steps, task associations, file types, and more.

.. http:post:: /zeafrost/api/v1/publishedfile/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/publishedfile/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific published file. Use this parameter to retrieve details for a single published file.
    :<json str code: Filter published files based on a specific code or identifier.
    :<json str entity: Filter published files based on the type of entity associated with the file.
    :<json str project: Filter published files based on the unique identifier or name of the project to which they belong.
    :<json str step: Filter published files based on the specific step or phase of the workflow.
    :<json str[] steps: An array of step names. Use this parameter to filter published files based on multiple steps simultaneously.
    :<json str task:  Filter published files based on the unique identifier or name of the associated task.
    :<json str type: Filter published files based on a specific type or category.
    :<json str[] types: An array of types. Use this parameter to filter published files based on multiple types simultaneously.
    :<json str publish_type: Filter published files based on a specific publish type, similar to ``type``.
    :<json str[] publish_types: An array of publish types. Use this parameter to filter published files based on multiple publish types simultaneously, similar to ``types``.
    :<json str publish_file: Filter published files based on the unique identifier or name of a specific published file.
    :<json str[] publish_files: An array of published file identifiers. Use this parameter to filter published files based on multiple files simultaneously.
    :<json int[] asset_ids: An array of asset identifiers. Use this parameter to filter published files based on multiple assets simultaneously.
    :<json str namespace: Filter published files based on a specific namespace.
    :<json str version_code: Filter published files based on a specific version code.
    :<json str version_number:  Filter published files based on a specific version number.
    :<json str path_to_movie: Filter published files based on the path to the movie file.
    :<json str path_to_frames: Filter published files based on the path to the frames files.
    :<json bool latest: Retrieve the latest published files if set to ``true``. Default is ``false``
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``publishedFile`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``publishedFile``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.