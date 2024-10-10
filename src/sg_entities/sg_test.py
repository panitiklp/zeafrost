import threading
import time
import asyncio
from pprint import pprint

from ..sg_controllers import sg_con

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def fx_search_all_task():
    sg = sg_con.connect()
    result = sg.find(
        'Task',
        filters = [
            ['project.Project.name', 'is', 'PNTY'],
            ['step.Step.code', 'is', 'FX']
        ],
        fields = [
            'code',
            'entity.Shot.code',
            'entity.Shot.id',
            'entity.Shot.sg_episode.Episode.code',
            'entity.Shot.sg_episode.Episode.id',
            'entity.Shot.sg_sequence.Sequence.code',
            'entity.Shot.sg_sequence.Sequence.id'
        ]
    )

    return result

