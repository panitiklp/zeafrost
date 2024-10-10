PROJECT_DIRECTORIES = [
    '.pdc',
    'commu/cln/in',
    'commu/cln/out',
    'dialy',
    'delivery/asset',
    'delivery/shot',
    'doc',
    'edit/export',
    'edit/footage',
    'edit/project',
    'lib',
    'pip',
    'private',
    'publish/asset',
    'publish/shot',
    'release/asset',
    'release/shot',
    'review/asset',
    'review/shot',
    'work/asset',
    'work/shot',
    'publish/asset/{type}',
    'work/asset/{type}',
    'review/asset/{type}',
    'release/asset/{type}',
]

EPISODE_DIRECTORIES = [
    'work/shot/{ep}',
    'review/shot/{ep}',
    'publish/shot/{ep}',
    'release/shot/{ep}'
]

SEQUENCE_DIRECTORIES = [
    'work/shot/{ep}/{seq}',
    'review/shot/{ep}/{seq}',
    'publish/shot/{ep}/{seq}',
    'release/shot/{ep}/{seq}'
]

SHOT_DIRECTORIES = [
    'work/shot/{ep}/{seq}/{shot}/{step}/{dcc}/{elem}',
    'review/shot/{ep}/{seq}/{shot}/{step}',
    'publish/shot/{ep}/{seq}/{shot}/{step}',
    'release/shot/{ep}/{seq}/{shot}/{reltype}'
]

ASSET_DIRECTORIES = [
    'work/asset/{type}/{asset}/{step}/{dcc}/{elem}',
    'review/asset/{type}/{asset}/{step}',
    'publish/asset/{type}/{asset}/{step}',
    'release/asset/{type}/{asset}/{step}'
]

STEP_DCC_DIRECTORIES = {
    'shot':{
        'lay':[
            'maya'
        ],
        'anm':[
            'maya'
        ],
        'cfx':[
            'maya',
            'hou'
        ],
        'lgt':[
            'maya',
            'nuke'
        ],
        'fx':[
            'maya',
            'hou',
            'nuke'
        ],
        'cmp':[
            'nuke'
        ]
    },
    'asset':{
        'model':[
            'maya',
            'zbr'
        ],
        'look':[
            'maya',
            'nuke'
        ],
        'tex':[
            'maya',
            'ps',
            'spp'
        ],
        'rig': [
            'maya'
        ],
        'simrig':[
            'maya',
            'hou'
        ],
        'drs':[
            'maya',
            'hou'
        ]
    }
}

DCC_ELEM_DIRECTORIES = {
    'maya': [
        'scenes',
        'output',
        'data',
        'wip'
    ],
    'nuke':[
        'scenes',
        'output',
        'data',
        'wip'
    ],
    'hou':[
        'scenes',
        'output',
        'data',
        'wip'
    ],
    'ps':[
        'scenes',
        'output',
        'data',
        'wip'
    ],
    'spp':[
        'scenes',
        'output',
        'data',
        'wip'
    ],
    'zbr':[
        'scenes',
        'output',
        'data',
        'wip'
    ]
}
    
RELEASE_TYPE_DIRECTORIES = {
    'shot': [
        'abc',
        'curves',
        'dljob',
        'dbpy',
        'furcache',
        'fxguide',
        'shotset'
    ],
    'asset': []
}

DEFAULT_ASSET_TYPE_DIRECTORIES = [
    'cam',
    'char',
    'prop',
    'vhcl',
    'set',
    'scat',
    'dmp',
    'trn',
    'sky'
]