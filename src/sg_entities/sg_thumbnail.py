from ..sg_controllers import sg_con

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    project = body.get('project')
    entity = body.get('entity') or 'shot'
    episode = body.get('episode')

    sg_filters = []
    result = []

    if project:
        sg_filters += [['project', 'name_contains', project]]
    if episode:
        sg_filters += [['sg_episode', 'name_contains', episode]]

    if sg_filters:
        sg = sg_con.connect()
        result = sg.find(
            entity.title(),
            filters=sg_filters,
            fields=['image']
        )

    return result
