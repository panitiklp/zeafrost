=============
Project
=============

search
-------------------

search by project
^^^^^^^^^^^^^^^^^^^

.. http:post:: /zeafrost/api/v1/project/search

    **Example request**:

        headers

        .. sourcecode:: http

            POST /zeafrost/api/v1/project/search HTTP/1.1
            Host: http://pip-oceanus
            Accept: application/json

        payload

        .. sourcecode:: json

            {
                "project": "zeafrost"
            }

    **Example response**:

        header

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Vary: Accept
            Content-Type: application/json
        
        response
        
        .. sourcecode:: text

            [
                {
                    "project":"zeafrost",
                    .
                    .
                    .
                }
            ]

search by id
^^^^^^^^^^^^^^^

.. http:post:: /zeafrost/api/v1/project/search

    **Example request**:

        headers

        .. sourcecode:: http

            POST /zeafrost/api/v1/project/search HTTP/1.1
            Host: http://pip-oceanus
            Accept: application/json

        payload

        .. sourcecode:: json

            {
                "id": 6348
            }

    **Example response**:

        header

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Vary: Accept
            Content-Type: application/json
        
        response
        
        .. sourcecode:: text

            [
                {
                    "project":"zeafrost",
                    .
                    .
                    .
                }
            ]