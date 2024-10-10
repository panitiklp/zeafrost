=========================
PipelineConfiguration
=========================

search
------------

  The pipelineConfiguration search endpoint allows users to dynamically search for pipeline configurations within the designated projects. 
  This functionality provides a flexible way to find configurations that match specific attributes, including project associations, version numbers, descriptions, and the unique identifier or name of the associated software.

.. http:post:: /zeafrost/api/v1/software/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/software/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific pipeline configuration. Use this parameter to retrieve details for a single configuration.
    :<json str project: Filter configurations based on the unique identifier or name of the project to which they belong.
    :<json str version: Filter configurations based on the version number or identifier.
    :<json str description: Filter configurations based on a specific description or summary.
    :<json str software: Filter configurations based on the unique identifier or name of the associated software.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``pipelineConfiguration`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``pipelineConfiguration``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.
