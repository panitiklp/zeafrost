==========
Task
==========

search
-------------------

  The task search endpoint allows users to perform dynamic searches for tasks within the designated projects. 
  Users can efficiently locate tasks based on various attributes, including the task name, unique identifier, associated assets, shots, or specific steps in the workflow.

.. http:post:: /zeafrost/api/v1/task/search

    **Request**:

        `Headers`

            .. sourcecode:: http

                POST /zeafrost/api/v1/task/search HTTP/1.1
                Host: http://pip-oceanus
                Accept: application/json
                Content-Type: application/json
    
    :<json int id: The unique identifier of a specific task. Use this parameter to retrieve details for a single task.
    :<json str project: Filter tasks based on the unique identifier or name of the project to which they belong.
    :<json str asset_type: Filter tasks based on the type or category of the asset associated with the task.
    :<json str asset: Filter tasks based on the unique identifier or name of the asset to which they are associated.
    :<json str episode: Filter tasks based on the unique identifier or name of the episode to which they belong.
    :<json str sequence: Filter tasks based on the unique identifier or name of the sequence to which they belong.
    :<json str shot: Filter tasks based on the unique identifier or name of the shot to which they are associated.
    :<json str variation: Filter tasks based on a specific variation or version.
    :<json str step: Filter tasks based on the specific step or phase of the workflow.
    :<json str[] steps: An array of step names. Use this parameter to filter tasks based on multiple steps simultaneously.
    :<json str task: Filter tasks based on the unique identifier or name of a specific task.
    :<json bool shotgrid: If set to ``true``, the response includes raw ShotGrid data. Default is ``false``
    
    ----------------------------------------------------

    **Response**:

    :>jsonarr int code: The HTTP status code indicating the success or failure of the request.
    :>jsonarr json[] data:  An array containing ``task`` details.
    :>jsonarr str entity:  Indicates the type of entity being returned (e.g., ``task``).
    :>jsonarr json payload: The payload included in the request.
    :>jsonarr str timestamp: The timestamp indicating when the response was generated.