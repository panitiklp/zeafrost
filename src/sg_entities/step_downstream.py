step_downstream = {
    "step":{
        "model":{
            "downstream":["tex", "look", "rig", "fur"]
        },
        "tex":{
            "downstream":["look", "fur"]
        },
        "look":{
            "downstream":["fur"]
        },
        "fur":{
            "downstream":[]
        },
        "rig":{
            "downstream":["anm"]
        },
        "simrig":{
            "downstream":[]
        },
        "drs":{
            "downstream":["lay"]
        },
        "lay":{
            "downstream":["anm", "lgt", "fx"]
        },
        "anm":{
            "downstream":["lgt", "fx", "cmp", "cfx"]
        },
        "cfx":{
            "downstream":["lgt"]
        },
        "fx":{
            "downstream":["lgt", "cmp"]
        },
        "lgt":{
            "downstream":["lgt"]
        },
        "cmp":{
            "downstream":[]
        }
    }
}