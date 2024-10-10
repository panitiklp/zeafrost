from collections import OrderedDict

from . import mongo_base
from .. import gen_utils
from ..redis_controllers import redis_ctl, redis_utils

PROJECT_AREAS = [
    'work',
    'review',
    'publish',
    'deliverable'
]

API_TIMEZONE = 'Asia/Bangkok'

class ZeafrostProject(mongo_base.ZeafrostDb):
    def __init__(self, *args, **kwargs):
        super(ZeafrostProject, self).__init__(*args, **kwargs)
        self.collection = self.db['project']
    
    def schema_basic_information(self, project_code=None, project_id=None, status='active', shotgrid_id=None):
        result = OrderedDict()
        result['id'] = project_id
        result['code'] = project_code
        result['shotgrid_id'] = shotgrid_id
        result['is_active'] = True

        return result
    
    def schema_resolution(self, preview, review, deliverable):
        result = OrderedDict()
        result['preview'] = preview or [1920, 1080]
        result['review'] = review or [1920, 1080]
        result['deliverable'] = deliverable or [1920, 1080]

        return result
    
    def schema_asset_type(self):
        result = OrderedDict()
        result['char'] = OrderedDict()
        result['char']['display_name'] = 'char'
        result['char']['description'] = 'Character'

        result['prop'] = OrderedDict()
        result['prop']['display_name'] = 'prop'
        result['prop']['description'] = 'Prop'

        result['vhcl'] = OrderedDict()
        result['vhcl']['display_name'] = 'vhcl'
        result['vhcl']['description'] = 'Vehicle'

        result['set'] = OrderedDict()
        result['set']['display_name'] = 'set'
        result['set']['description'] = 'Set'

        result['dmp'] = OrderedDict()
        result['dmp']['display_name'] = 'dmp'
        result['dmp']['description'] = 'Digital Mattepaint'

        result['trn'] = OrderedDict()
        result['trn']['display_name'] = 'trn'
        result['trn']['description'] = 'Terrain'

        result['scat'] = OrderedDict()
        result['scat']['display_name'] = 'scat'
        result['scat']['description'] = 'Scatter'

        result['fx'] = OrderedDict()
        result['fx']['display_name'] = 'fx'
        result['fx']['description'] = 'FX'

        result['lgt'] = OrderedDict()
        result['lgt']['display_name'] = 'lgt'
        result['lgt']['description'] = 'Light'

        result['cmb'] = OrderedDict()
        result['cmb']['display_name'] = 'cmb'
        result['cmb']['description'] = 'Combine'

        result['lightset'] = OrderedDict()
        result['lightset']['display_name'] = 'lightset'
        result['lightset']['description'] = 'Light Set'

        return result
    
    def schema_directory(self, project_path):
        result = OrderedDict()
        result['work'] = OrderedDict()
        result['work']['asset'] = f'{project_path}/work/asset'
        result['work']['shot'] = f'{project_path}/work/shot'

        result['review'] = OrderedDict()
        result['review']['asset'] = f'{project_path}/review/asset'
        result['review']['shot'] = f'{project_path}/review/shot'

        result['publish'] = OrderedDict()
        result['publish']['asset'] = f'{project_path}/publish/asset'
        result['publish']['shot'] = f'{project_path}/publish/shot'

        result['deliverable'] = OrderedDict()
        result['deliverable']['asset'] = f'{project_path}/deliverable/asset'
        result['deliverable']['shot'] = f'{project_path}/deliverable/shot'

        return result
    
    def schema_pattern_version(self):
        result = OrderedDict()
        result['prefix'] = 'v'
        result['padding'] = 3

        return result
    
    def schema_pattern_asset(self):
        result = OrderedDict()
        result['longname'] = '{name}'
        result['shortname'] = '{name}'
        result['first_char'] = 'lower'
        result['regular_expression'] = '[a-z]+\w+'

        return result
    
    def schema_pattern_episode(self):
        result = OrderedDict()
        result['prefix'] = ''
        result['longname'] = '{episode}'
        result['shortname'] = '{episode}'

        return result
    
    def schema_pattern_sequence(self):
        result = OrderedDict()
        result['prefix'] = ''
        result['longname'] = '{episode}_{sequence}'
        result['shortname'] = '{sequence}'

        return result
    
    def schema_pattern_shot(self):
        result = OrderedDict()
        result['prefix'] = ''
        result['longname'] = '{project}_{episode}_{sequence}_{shot}'
        result['shortname'] = '{shot}'

        return result
    
    def schema_pattern_file_name(self):
        result = OrderedDict()
        result['scene'] = OrderedDict()
        result['scene']['work'] = OrderedDict()
        result['scene']['work']['asset'] = '{asset}_{step}_{task}_{version}.{ext}'
        result['scene']['work']['shot'] = '{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}'

        return result
    
    def schema_pattern_node_asset(self):
        # ------------------------- #
        #       OBJECT PATTERN      #
        # ------------------------- #
        result = OrderedDict()
        result['top_node'] = '{asset}_GRP'
        result['naming_style'] = 'camel'
        result['digit_padding'] = 3
        result['cacheable_node'] = 'geo_grp'
        result['name'] = '{component}_{node_type}'
        result['name_multi'] = '{component}_{digit}_{node_type}'
        result['name_side'] = '{component}_{side}_{node_type}'
        result['name_side_multi'] = '{component}_{side}_{digit}_{node_type}'

        # --------------- #
        #       SIDE      #
        # --------------- #
        result['side'] = OrderedDict()
        result['side']['left'] = 'LT'
        result['side']['right'] = 'RT'

        # ----------------- #
        #       SUFFIX      #
        # ----------------- #
        result['suffix'] = OrderedDict()
        result['suffix']['group'] = 'GRP'
        result['suffix']['mesh'] = 'GEO'
        result['suffix']['shader'] = 'SHD'
        result['suffix']['file'] = 'FILE'
        result['suffix']['nurbsCurve'] = 'CRV'
        result['suffix']['controller'] = 'CTRL'

        # --------------------- #
        #       MAP TYPE        #
        # --------------------- #
        result['map_type'] = OrderedDict()
        result['map_type']['color'] = 'COL'
        result['map_type']['specular'] = 'SPEC'
        result['map_type']['displacement'] = 'DIS'
        result['map_type']['normal'] = 'NRM'
        result['map_type']['isolation'] = 'ISO'
        result['map_type']['height'] = 'HEIGHT'
        result['map_type']['metallic'] = 'METAL'

        # ------------------------------- #
        #       REGULAR EXPRESSION        #
        # ------------------------------- #
        result['regular_expression'] = OrderedDict()
        result['regular_expression']['asset'] = '([a-zA-Z_0-9]+)'
        result['regular_expression']['asset_type'] = '([a-z]+)'
        result['regular_expression']['step'] = '(model|look|rig|simrig|tex|fur|drs)'
        result['regular_expression']['task'] = '([a-zA-Z0-9]+)'
        result['regular_expression']['extension'] = '([a-z0-9]+)'
        result['regular_expression']['component'] = '([a-zA-Z_0-9]+)'
        result['regular_expression']['suffix'] = '([A-Z]+)'
        result['regular_expression']['side'] = '([A-Z]{2})'
        result['regular_expression']['digit'] = '([0-9]{3})'
        result['regular_expression']['map_type'] = '([A-Z]+)'

        return result
    
    def schema_pattern_node_shot(self):
        result = OrderedDict()
        result['suffix'] = OrderedDict()
        result['regular_expression'] = OrderedDict()
        result['regular_expression']['project'] = '([A-Z0-9]+)'
        result['regular_expression']['episode'] = '([A-Z0-9]+)'
        result['regular_expression']['sequence'] = '([sS][0-9A-Z]+)'
        result['regular_expression']['shot'] = '([A-Z0-9]+)'
        result['regular_expression']['step'] = '(lay|anm|lgt|cfx|fx|cmp)'
        result['regular_expression']['task'] = '([a-zA-Z0-9_]+)'
        result['regular_expression']['extension'] = '([a-z]+)'

        return result
    
    # -------------------------- #
    #       WORK TEMPLATE        #
    # -------------------------- #
    def schema_pattern_asset_work(self, directory, file_name, file_extension):
        result = OrderedDict()
        result['directory'] = directory
        result['file_name'] = file_name
        result['file_extension'] = file_extension

        return result

    # ---------------------------- #
    #       REVIEW TEMPLATE        #
    # ---------------------------- #
    def schema_pattern_review(self, directory, file_name, file_extension, media_type, codec=None):
        result = OrderedDict()
        result['directory'] = directory
        
        if media_type == 'movie':
            result['file_name'] = file_name
            result['file_extension'] = file_extension
            result['codec'] = codec

        elif media_type == 'image':
            result['file_name'] = file_name
            result['file_extension'] = file_extension

        return result
    
    # ----------------------------- #
    #       PUBLISH TEMPLATE        #
    # ----------------------------- #
    def schema_pattern_publish(self, published_type, directory, file_name, file_extension, codec=None):
        result = OrderedDict()
        result['type'] = published_type
        result['directory'] = directory
        result['file_name'] = file_name
        result['file_extension'] = file_extension

        if codec:
            result['codec'] = codec

        return result
        
    def schema_pattern_step_model(self):
        result = OrderedDict()
        result['display_name'] = 'model'
        result['entity_type'] = 'asset'
        result['description'] = 'Model'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )
        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/nuke/scene',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/{dcc}/output',
            file_name='{asset}_{step}_{task}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>> GEOMETRY <<< #
        result['production_area']['publish']['geometry'] = self.schema_pattern_publish(
            published_type='geometry', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>> UV <<< #
        result['production_area']['publish']['uv'] = self.schema_pattern_publish(
            published_type='uv', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>> GPU <<< #
        result['production_area']['publish']['gpu'] = self.schema_pattern_publish(
            published_type='gpu', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>> FBX <<< #
        result['production_area']['publish']['fbx'] = self.schema_pattern_publish(
            published_type='fbx', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='fbx'
        )

        # >>> PLACEHOLDERGEO <<< #
        result['production_area']['publish']['placeholdergeo'] = self.schema_pattern_publish(
            published_type='placeholdergeo', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='ma'
        )

        # >>> MATERIAL <<< #
        result['production_area']['publish']['material'] = self.schema_pattern_publish(
            published_type='material', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='ma'
        )

        # >>> MATERAIL DATA <<< #
        result['production_area']['publish']['material_metadata'] = self.schema_pattern_publish(
            published_type='material_metadata', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='json'
        )

        # >>> MAP RENDER <<< #
        result['production_area']['publish']['mapren'] = self.schema_pattern_publish(
            published_type='mapren', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='tif'
        )

        # >>> MAP PREVIEW <<< #
        result['production_area']['publish']['mapprev'] = self.schema_pattern_publish(
            published_type='mapprev', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='jpg'
        )

        # >>> MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>> THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )
        
        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_look(self):
        result = OrderedDict()
        result['display_name'] = 'look'
        result['entity_type'] = 'asset'
        result['description'] = 'Look Development'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )
        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/nuke/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/{dcc}/output',
            file_name='{asset}_{step}_{task}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  PLACEHOLDER <<< #
        result['production_area']['publish']['placeholder'] = self.schema_pattern_publish(
            published_type='placeholder', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='ma'
        )

        # >>>  REDSHIF RENDER PROXY <<< #
        result['production_area']['publish']['redshift_render_proxy'] = self.schema_pattern_publish(
            published_type='redshift_render_proxy', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='rs'
        )

        # >>>  ARNOLD RENDER PROXY <<< #
        result['production_area']['publish']['arnold_render_proxy'] = self.schema_pattern_publish(
            published_type='arnold_render_proxy', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ass'
        )

        # # >>>  PLACEHOLDERGEO <<< #
        # result['production_area']['publish']['placeholdergeo'] = self.schema_pattern_publish(
        #     published_type='placeholdergeo', 
        #     directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
        #     file_name='{asset}_{step}_{task}_{type}.{ext}', 
        #     file_extension='abc'
        # )

        # # >>>  RENDERPX <<< #
        # result['production_area']['publish']['renderpx'] = self.schema_pattern_publish(
        #     published_type='renderpx', 
        #     directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
        #     file_name='{asset}_{step}_{task}.{ext}', 
        #     file_extension='rs'
        # )

        # >>>  MATERAIL <<< #
        result['production_area']['publish']['mat'] = self.schema_pattern_publish(
            published_type='mat', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='ma'
        )

        # >>>  MATERAIL DATA <<< #
        result['production_area']['publish']['material_metadata'] = self.schema_pattern_publish(
            published_type='material_metadata', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='json'
        )

        # >>> UV <<< #
        result['production_area']['publish']['uv'] = self.schema_pattern_publish(
            published_type='uv', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>> FBX <<< #
        result['production_area']['publish']['fbx'] = self.schema_pattern_publish(
            published_type='fbx', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='fbx'
        )

        # >>>  MAP RENDER <<< #
        result['production_area']['publish']['mapren'] = self.schema_pattern_publish(
            published_type='mapren', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='tif'
        )

        # >>>  MAP PREVIEW <<< #
        result['production_area']['publish']['mapprev'] = self.schema_pattern_publish(
            published_type='mapprev', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='jpg'
        )

        # >>>  MAP BINARY COMPILED <<< #
        result['production_area']['publish']['mapbin'] = self.schema_pattern_publish(
            published_type='mapbin', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='rstexbin'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_tex(self):
        result = OrderedDict()
        result['display_name'] = 'tex'
        result['entity_type'] = 'asset'
        result['description'] = 'Texture'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )
        
        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/nuke/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/{dcc}/output',
            file_name='{asset}_{step}_{task}.####.{ext}',
            file_extension='exr'
        )
        

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        result['production_area']['publish']['scene']['substance_painter'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='spp'
        )

        # >>>  MAP RENDER <<< #
        result['production_area']['publish']['mapren'] = self.schema_pattern_publish(
            published_type='mapren', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='tif'
        )

        # >>>  MAP PREVIEW <<< #
        result['production_area']['publish']['mapprev'] = self.schema_pattern_publish(
            published_type='mapprev', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='jpg'
        )

        # >>>  MAP BINARY COMPILED <<< #
        result['production_area']['publish']['mapbin'] = self.schema_pattern_publish(
            published_type='mapbin', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}/sourceimages', 
            file_name='{map_name}_{map_type}_{colorspace}.{udim}.{ext}', 
            file_extension='rstexbin'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_rig(self):
        result = OrderedDict()
        result['display_name'] = 'rig'
        result['entity_type'] = 'asset'
        result['description'] = 'Rig'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>> FBX <<< #
        result['production_area']['publish']['fbx'] = self.schema_pattern_publish(
            published_type='fbx', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='fbx'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_simrig(self):
        result = OrderedDict()
        result['display_name'] = 'simrig'
        result['entity_type'] = 'asset'
        result['description'] = 'Simulation Rig'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )
        result['production_area']['work']['scene']['houdini'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/hou/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='hip'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        result['production_area']['publish']['scene']['houdini'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='hip'
        )

        # >>> FBX <<< #
        result['production_area']['publish']['fbx'] = self.schema_pattern_publish(
            published_type='fbx', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='fbx'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] =self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_fur(self):
        result = OrderedDict()
        result['display_name'] = 'fur'
        result['entity_type'] = 'asset'
        result['description'] = 'Fur'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        result['production_area']['work']['scene']['houdini'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/hou/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='hip'
        )

        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/nuke/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/{dcc}/output',
            file_name='{asset}_{step}_{task}.####.{ext}',
            file_extension='exr'
        )
       
        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  FUR NODE <<< #
        result['production_area']['publish']['furnode'] = self.schema_pattern_publish(
            published_type='furnode', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='ma'
        )

        # >>>  YETI NODE <<< #
        result['production_area']['publish']['yeti_node'] = self.schema_pattern_publish(
            published_type='yeti_node', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}"', 
            file_extension='ma'
        )

        # >>>  GEO GUIDE <<< #
        result['production_area']['publish']['geo_guide'] = self.schema_pattern_publish(
            published_type='geo_guide', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>>  CURVE GUIDE <<< #
        result['production_area']['publish']['curve_guide'] = self.schema_pattern_publish(
            published_type='curve_guide', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>>  FUR SHELL <<< #
        result['production_area']['publish']['fur_shell'] = self.schema_pattern_publish(
            published_type='fur_shell', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='abc'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_drs(self):
        result = OrderedDict()
        result['display_name'] = 'drs'
        result['entity_type'] = 'asset'
        result['description'] = 'Dressing'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/maya/scenes',
            file_name='{asset}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{asset_type}/{asset}/{step}/{dcc}/output',
            file_name='{asset}_{step}_{task}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{asset_type}/{asset}/{step}', 
            file_name='{asset}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  SET DATA <<< #
        result['production_area']['publish']['setdata'] = self.schema_pattern_publish(
            published_type='setdata', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='json'
        )

        # >>>  SHOT SET <<< #
        result['production_area']['publish']['shot_set'] = self.schema_pattern_publish(
            published_type='shot_set', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}__{type}.{ext}', 
            file_extension='json'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{asset_type}/{asset}/{step}/{task}/{version}', 
            file_name='{asset}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # >>>  THUMBNAIL <<< #
        result['production_area']['publish']['media']['thumbnail'] = self.schema_pattern_publish(
            published_type='thumbnail', 
            directory='{root}/{asset_type}/{asset}/thumbnail', 
            file_name='datetimestamp__{step}.{ext}', 
            file_extension='png'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_lay(self):
        result = OrderedDict()
        result['display_name'] = 'lay'
        result['entity_type'] = 'shot'
        result['description'] = 'Layout'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/maya/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()
        
        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  SHOT SET USD <<< #
        result['production_area']['publish']['shotset_usd'] = self.schema_pattern_publish(
            published_type='shotset_usd', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset_usd', 
            file_name='{namespace}___{asset}_{type}.{ext}', 
            file_extension='usd'
        )

        # >>>  SHOT SET SCENE <<< #
        result['production_area']['publish']['shot_set_scene'] = self.schema_pattern_publish(
            published_type='shotset_scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset_scene', 
            file_name='{namespace}___{asset}_{type}.{ext}', 
            file_extension='ma'
        )

        # >>>  SHOT SET <<< #
        result['production_area']['publish']['shotset'] = self.schema_pattern_publish(
            published_type='shotset', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset', 
            file_name='{namespace}___{asset}_{type}.{ext}', 
            file_extension='json'
        )

        # >>>  SEQUENCER <<< #
        result['production_area']['publish']['sequencer'] = self.schema_pattern_publish(
            published_type='sequencer', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/sequencer', 
            file_name='{project}_{episode}_{sequence}_{shot}_{type}.{ext}', 
            file_extension='json'
        )

        # >>>  ANIM CURVE <<< #
        result['production_area']['publish']['animation_curve'] = self.schema_pattern_publish(
            published_type='animation_curve', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/animation_curve', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='anim'
        )

        # >>>  ANIM CACHE ABC <<< #
        result['production_area']['publish']['animation_cache_abc'] = self.schema_pattern_publish(
            published_type='animation_cache_abc', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/animation_cache_abc', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='abc'
        )
        
        # >>>  FUR CACHE <<< #
        result['production_area']['publish']['furcache'] = self.schema_pattern_publish(
            published_type='furcache', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/furcache', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='fur'
        )

        # >>>  FUR CACHE <<< #
        result['production_area']['publish']['fxguide'] = self.schema_pattern_publish(
            published_type='fxguide', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/fxguide', 
            file_name='fxguide.{ext}', 
            file_extension='ma'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_anm(self):
        result = OrderedDict()
        result['display_name'] = 'anm'
        result['entity_type'] = 'shot'
        result['description'] = 'Animation'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/maya/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  SHOT SET <<< #
        result['production_area']['publish']['shotset'] = self.schema_pattern_publish(
            published_type='shotset', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='json'
        )

        # >>>  SHOT SET USD <<< #
        result['production_area']['publish']['shotset_usd'] = self.schema_pattern_publish(
            published_type='shotset_usd', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset_usd', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='usd'
        )

        # >>>  SHOT SET SCENE <<< #
        result['production_area']['publish']['shot_set_scene'] = self.schema_pattern_publish(
            published_type='shot_set_scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/shotset_scene', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='ma'
        )

        # >>>  ANIM CURVE <<< #
        result['production_area']['publish']['animation_curve'] = self.schema_pattern_publish(
            published_type='animation_curve', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/animcurve', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='anim'
        )

        # >>>  ANIM CACHE ABC <<< #
        result['production_area']['publish']['animation_cache_abc'] = self.schema_pattern_publish(
            published_type='animation_cache_abc', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/animcache', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='abc'
        )

        # >>>  FUR CACHE <<< #
        result['production_area']['publish']['furcache'] = self.schema_pattern_publish(
            published_type='furcache', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/furcache', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='fur'
        )

        # >>>  FUR GUIDE <<< #
        result['production_area']['publish']['fxguide'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/fxguide', 
            file_name='{namespace}___{asset}.{ext}', 
            file_extension='ma'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_cfx(self):
        result = OrderedDict()
        result['display_name'] = 'cfx'
        result['entity_type'] = 'shot'
        result['description'] = 'Character FX'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/maya/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        result['production_area']['work']['scene']['houdini'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/hou/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='hip'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov', 
            codec='H.264'
        )
        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        result['production_area']['publish']['scene']['houdini'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='hip'
        )

        # >>>  ANIM CACHE <<< #
        result['production_area']['publish']['animcache'] = self.schema_pattern_publish(
            published_type='animcache', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/animcache', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='abc'
        )

        # >>>  FUR CACHE <<< #
        result['production_area']['publish']['furcache'] = self.schema_pattern_publish(
            published_type='furcache', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/furcache', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='fur'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = self.schema_pattern_publish(
            published_type='furcache', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result

    def schema_pattern_step_lgt(self):
        result = OrderedDict()
        result['display_name'] = 'lgt'
        result['entity_type'] = 'shot'
        result['description'] = 'Light'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/maya/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/nuke/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{dcc}/output/{render_layer}/{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}',
            file_name='{render_layer}_{colorspace}.{aov}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['image'] = self.schema_pattern_review(
            media_type='image', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}_{colorspace}.####.{ext}', 
            file_extension='exr'
        )
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result
    
    def schema_pattern_step_fx(self):
        result = OrderedDict()
        result['display_name'] = 'fx'
        result['entity_type'] = 'shot'
        result['description'] = 'FX'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['maya'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/maya/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='ma'
        )

        result['production_area']['work']['scene']['houdini'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/hou/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/nuke/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{dcc}/output/{render_layer}/{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}',
            file_name='{render_layer}_{colorspace}.{aov}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['image'] = self.schema_pattern_review(
            media_type='image', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}_{colorspace}.####.{ext}', 
            file_extension='exr'
        )
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['maya'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='ma'
        )

        # >>>  VDB <<< #
        result['production_area']['publish']['vdb'] = self.schema_pattern_publish(
            published_type='vdb', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/vdb', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='vdb'
        )

        # >>>  RENDER PROXY <<< #
        result['production_area']['publish']['renderpx'] = self.schema_pattern_publish(
            published_type='renderpx', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}/{type}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='rs'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result
    
    def schema_pattern_step_cmp(self):
        result = OrderedDict()
        result['display_name'] = 'cmp'
        result['entity_type'] = 'shot'
        result['description'] = 'Composite'
        result['production_area'] = OrderedDict()

        # ---- WORK ---- #
        result['production_area']['work'] = OrderedDict()
        result['production_area']['work']['scene'] = OrderedDict()
        result['production_area']['work']['output'] = OrderedDict()

        result['production_area']['work']['scene']['nuke'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/nuke/scenes',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}',
            file_extension='nk'
        )

        result['production_area']['work']['output']['render'] = self.schema_pattern_asset_work(
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{dcc}/output',
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}_{colorspace}.####.{ext}',
            file_extension='exr'
        )

        # ---- REVIEW ---- #
        result['production_area']['review'] = OrderedDict()
        result['production_area']['review']['media'] = OrderedDict()
        result['production_area']['review']['media']['image'] = self.schema_pattern_review(
            media_type='image', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}_{colorspace}.####.{ext}', 
            file_extension='exr'
        )
        result['production_area']['review']['media']['movie'] = self.schema_pattern_review(
            media_type='movie', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}_{version}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- PUBLISH ---- #
        result['production_area']['publish'] = OrderedDict()

        # >>>  SCENE <<< #
        result['production_area']['publish']['scene'] = OrderedDict()
        result['production_area']['publish']['scene']['nuke'] = self.schema_pattern_publish(
            published_type='scene', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='nk'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['image'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.####.{ext}', 
            file_extension='exr'
        )

        # >>>  MEDIA <<< #
        result['production_area']['publish']['media'] = OrderedDict()
        result['production_area']['publish']['media']['image'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.####.{ext}', 
            file_extension='exr'
        )
        result['production_area']['publish']['media']['movie'] = self.schema_pattern_publish(
            published_type='media', 
            directory='{root}/{episode}/{sequence}/{shot}/{step}/{task}/{version}', 
            file_name='{project}_{episode}_{sequence}_{shot}_{step}_{task}.{ext}', 
            file_extension='mov',
            codec='H.264'
        )

        # ---- DELIVERABLE ---- #
        result['production_area']['deliverable'] = OrderedDict()

        return result
    
    def schema_validate_model(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "shape_name", 
                "duplicated_name", 
                "construction_history", 
                "lambert1_connection"
            ]
        result['optional'] = [ 
                "display_layer", 
                "anim_layer", 
                "render_layer", 
                "sets", 
                "reference", 
                "namespace", 
                "lock_node", 
                "map_border_edge", 
                "soft_edge", 
                "freeze_transform", 
                "deformed_node"
            ]
        
        return result
    
    def schema_validate_tex(self):
        result= OrderedDict()
        result['required'] = []
        result['optional'] = []
        
        return result
    
    def schema_validate_rig(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "shape_name", 
                "lambert1_connection"
            ]
        result['optional'] = [ 
                "anim_layer", 
                "render_layer", 
                "reference", 
                "namespace", 
                "lock_node"
            ]
        
        return result
    
    def schema_validate_look(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "shape_name", 
                "duplicated_name", 
                "construction_history", 
                "lambert1_connection"
            ]
        result['optional'] = [ 
                "display_layer", 
                "anim_layer", 
                "render_layer", 
                "sets", 
                "reference", 
                "namespace", 
                "lock_node", 
                "map_border_edge", 
                "soft_edge", 
                "freeze_transform", 
                "deformed_node"
            ]
        
        return result
    
    def schema_validate_fur(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "lambert1_connection"
            ]
        result['optional'] = []
        
        return result
    
    def schema_validate_simrig(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "shape_name", 
                "duplicated_name", 
                "lambert1_connection"
            ]
        result['optional'] = [ 
                "display_layer", 
                "anim_layer", 
                "render_layer", 
                "reference", 
                "namespace", 
                "lock_node"
            ]
        
        return result
    
    def schema_validate_drs(self):
        result= OrderedDict()
        result['required'] =  [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "lambert1_connection"
            ]
        result['optional'] = [ 
                "anim_layer", 
                "render_layer", 
                "sets", 
                "deformed_node"
            ]
        
        return result
    
    def schema_validate_lay(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "frame_rate"
            ]
        result['optional'] = [ 
                "unload_sub_reference"
            ]
        
        return result
    
    def schema_validate_anm(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "frame_rate"
            ]
        result['optional'] = [ 
                "unload_sub_reference", 
                "frame_range"
            ]
        
        return result
    
    def schema_validate_cfx(self):
        result= OrderedDict()
        result['required'] = [ 
                "unknown_node", 
                "unknown_plugin", 
                "malicious", 
                "frame_rate"
            ]
        result['optional'] = []
        
        return result
    
    def schema_validate_fx(self):
        result= OrderedDict()
        result['required'] = []
        result['optional'] = []
        
        return result
    
    def schema_validate_lgt(self):
        result= OrderedDict()
        result['required'] = []
        result['optional'] = []
        
        return result
    
    def schema_validate_cmp(self):
        result= OrderedDict()
        result['required'] = []
        result['optional'] = []
        
        return result
    
    def schema_step_policy_cmp(self):
        result = OrderedDict()
        result['software'] = OrderedDict()
        result['software']['nuke'] = OrderedDict()
        result['software']['nuke']['setup'] = OrderedDict()
        result['software']['nuke']['setup']['aces'] = 'acescg'
        result['software']['nuke']['setup']['aces_version'] = '1.2'
        result['software']['nuke']['setup']['channels'] = 'rgb'
        result['software']['nuke']['setup']['codec'] = 'appr'
        result['software']['nuke']['setup']['color_management'] = 'OCIO'
        result['software']['nuke']['setup']['color_space_images'] = 'rendering'
        result['software']['nuke']['setup']['color_space_movie'] = 'Output - Rec.709'
        result['software']['nuke']['setup']['color_space_still'] = 'Output - Rec.709'
        result['software']['nuke']['setup']['ocio_config'] = 'W:/yggpipe/release/dccPlugins/ocio/aces_1.2/config.ocio'
        result['software']['nuke']['setup']['convert_for_client'] = True
        result['software']['nuke']['setup']['display_lut'] = 'Rec.709 (ACES)'
        result['software']['nuke']['setup']['file_type_image'] = 'exr'
        result['software']['nuke']['setup']['file_type_movie'] = 'mov'
        result['software']['nuke']['setup']['setting'] = "'''WriteClinent['mov_prores_codec_profile'].setValue('ProRes 4:4:4:4 12-bit')'''"
        result['software']['nuke']['setup']['setting_enable'] = True
        result['software']['nuke']['setup']['setting_images'] = False
        result['software']['nuke']['setup']['resolution_delivery'] = '1920 1080'
        result['software']['nuke']['setup']['reolution_format'] = '1920 1080 DEFAULT'
        result['software']['nuke']['setup']['nuke_version'] = 'Nuke13.1V1'

        return result

    def schema_to_document(self, **kwargs):
        project_id = kwargs.get('project_id')
        project_code = kwargs.get('project_code')
        status = kwargs.get('status') or 'active'
        shotgrid_id = kwargs.get('shotgrid_id')
        resolution = kwargs.get('resolution')
        project_path = kwargs.get('project_path')
        username = kwargs.get('username')

        current_datetime = gen_utils.get_timestamp(API_TIMEZONE)

        result = self.schema_basic_information(
            project_code=project_code, 
            project_id=project_id, 
            status=status, 
            shotgrid_id=shotgrid_id
        )
        result['resolution'] = self.schema_resolution(
            preview=resolution.get('preview') if resolution else None, 
            review=resolution.get('review') if resolution else None, 
            deliverable=resolution.get('delverable') if resolution else None
        )
        result['asset_type'] = self.schema_asset_type()
        result['directory'] = self.schema_directory(project_path=project_path)
        result['pattern'] = OrderedDict()
        result['pattern']['version'] = self.schema_pattern_version()
        result['pattern']['asset'] = self.schema_pattern_asset()
        result['pattern']['episode'] = self.schema_pattern_episode()
        result['pattern']['sequence'] = self.schema_pattern_sequence()
        result['pattern']['shot'] = self.schema_pattern_shot()
        result['pattern']['file_name'] = self.schema_pattern_file_name()
        result['pattern']['node'] = OrderedDict()
        result['pattern']['node']['asset'] = OrderedDict()
        result['pattern']['node']['asset'] = self.schema_pattern_node_asset()
        result['pattern']['node']['shot'] = OrderedDict()
        result['pattern']['node']['shot'] = self.schema_pattern_node_shot()
        result['pattern']['step'] = OrderedDict()
        result['pattern']['step']['model'] = self.schema_pattern_step_model()
        result['pattern']['step']['look'] = self.schema_pattern_step_look()
        result['pattern']['step']['tex'] = self.schema_pattern_step_tex()
        result['pattern']['step']['rig'] = self.schema_pattern_step_rig()
        result['pattern']['step']['simrig'] = self.schema_pattern_step_simrig()
        result['pattern']['step']['fur'] = self.schema_pattern_step_fur()
        result['pattern']['step']['drs'] = self.schema_pattern_step_drs()
        result['pattern']['step']['lay'] = self.schema_pattern_step_lay()
        result['pattern']['step']['anm'] = self.schema_pattern_step_anm()
        result['pattern']['step']['cfx'] = self.schema_pattern_step_cfx()
        result['pattern']['step']['lgt'] = self.schema_pattern_step_lgt()
        result['pattern']['step']['fx'] = self.schema_pattern_step_fx()
        result['pattern']['step']['cmp'] = self.schema_pattern_step_cmp()
        result['validation'] =  OrderedDict()
        result['validation']['model'] = self.schema_validate_model()
        result['validation']['tex'] = self.schema_validate_tex()
        result['validation']['look'] = self.schema_validate_look()
        result['validation']['fur'] = self.schema_validate_fur()
        result['validation']['rig'] = self.schema_validate_rig()
        result['validation']['simrig'] = self.schema_validate_simrig()
        result['validation']['drs'] = self.schema_validate_drs()
        result['validation']['lay'] = self.schema_validate_lay()
        result['validation']['anm'] = self.schema_validate_anm()
        result['validation']['lgt'] = self.schema_validate_lgt()
        result['validation']['cfx'] = self.schema_validate_cfx()
        result['validation']['fx'] = self.schema_validate_fx()
        result['validation']['cmp'] = self.schema_validate_cmp()
        result['step_policy'] =  OrderedDict()
        result['step_policy']['cmp'] = self.schema_step_policy_cmp()
        result['created_by'] = username
        result['created_at'] = current_datetime
        result['updated_by'] = username
        result['updated_at'] = current_datetime

        return result

def project_cache(project=''):

    filters = {}
    pattern_redis = 'zs:project:*'

    if project:
        filters = {'code' : {'$regex': project, '$options': 'i'}}
        pattern_redis = f'zs:project:{project}:*'

    project_db = ZeafrostProject()
    project_data = [each for each in project_db.find(filters)]
    project_db.close()

    redis_ctl.delete(pattern_redis)  

    redis_names = []
    for each_data in project_data:
        redis_name = f'zs:project:{each_data.get("code")}:{each_data.get("shotgrid_id")}'.lower()       # DEFINE REDIS NAME
        redis_ctl.delete(redis_name)  
        data_parse = redis_utils.redis_prepare_cache_data(each_data)
        redis_ctl.hset(redis_name, data_parse)                                  # REDIS CACHE - CMD: HSET

        redis_names.append(redis_name)
    
    return redis_names
