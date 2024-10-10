import unittest
import os
import sys

from pprint import pprint

MODULE = os.path.dirname(os.path.dirname(__file__))
if not MODULE in sys.path:
    sys.path.append(MODULE)

from src import main_ctl

class TestSearchProject(unittest.TestCase):

    # /////////////// #
    #     project     #
    # /////////////// #

    def test_find_all_project(self):

        payload = {}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_project_upper(self):

        payload = {'project': 'PNTY'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_project_lower(self):

        payload = {'project': 'pnty'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_project_camel(self):

        payload = {'project': 'pNtY'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_project_num_commercial(self):

        payload = {'project': '10_PKM'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])
        
    def test_find_project_no_num_commercial(self):

        payload = {'project': 'PKM'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])
            
    def test_find_wrong_project(self):

        payload = {'project': 'aaaa'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertEqual(result['data'], [])

    def test_find_type_project(self):

        payload = {'type': 'series'}
        entity = 'project'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertNotEqual(result['data'], [])


class TestSearchEpisode(unittest.TestCase):

    # /////////////// #
    #     episode     #
    # /////////////// #

    def test_find_episode(self):
        payload = {
            "project": "PNTY",
            "episode": "999" }
        entity = 'episode'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertNotEqual(result['data'], [])
        
    def test_find_episode_no_prject(self):
        payload = {"episode": "999" }
        entity = 'episode'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertNotEqual(result['data'], [])

    def test_find_all_episode_in_prject(self):
        payload = {"project": "pnty"}
        entity = 'episode'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertNotEqual(result['data'], [])

    def test_find_wrong_episode(self):
        payload = {
                "project": "pnty",
                "episode": "9898"
            }
        entity = 'episode'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertEqual(result['data'], [])


class TestSearchSequence(unittest.TestCase):

    # /////////////// #
    #     sequence    #
    # /////////////// #

    def test_find_sequence(self):
        payload = {'project': 'pnty', 'episode': '999', 'sequence': 'S99'}
        entity = 'sequence'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
        
        self.assertNotEqual(result['data'], [])

    def test_find_sequence_payload(self):
        # must be cache project
        payload = {'project': 'pnty', 'episode': '104'}
        entity = 'sequence'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_wrong_sequence(self):
        payload = {'project': 'pnty', 'episode': '104', 'sequence': '999'}
        entity = 'sequence'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertEqual(result['data'], [])


class TestSearchShot(unittest.TestCase):

    # /////////////// #
    #      shot       #
    # /////////////// #

    def test_find_shot(self):
        payload = {'project': 'pnty', 'episode': '104', 'sequence': 'S01', 'shot': '0010'}
        entity = 'shot'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_all_shot(self):
        payload = {'project': 'pnty', 'episode': '104'}
        entity = 'shot'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])

    def test_find_id_shot(self):
        payload = {'shot_id': 31232}
        entity = 'shot'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)


        self.assertNotEqual(result['data'], [])


class TestSearchTask(unittest.TestCase):

    # /////////////// #
    #      task       #
    # /////////////// #

    def test_find_task_all_shot(self):
        payload = {"project": "PIPEV2", "episode": "101", "sequence": "S01", "shot": "0010"}
        entity = 'task'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_task_assign(self):
        payload = {"user": "thaksaporn"}

        result = main_ctl.task_search_by_user(body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_task_assign_proj(self):
        payload = {"user": "thaksaporn", "project": "pipev2"}

        result = main_ctl.task_search_by_user(body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_task_from_status(self):
        payload = {"user": "warakorn", "status": "wtg"} # all project

        result = main_ctl.task_search_by_user(body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_tesk_wrong(self):
        payload = {"project": "PIPEV2", "episode": "101", "sequence": "S01", "shot": "0010", "task": "aaaa"}
        entity = 'task'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertEqual(result['data'], [])

    def test_find_tesk(self):
        payload = {
            "project": "PIPEV2", 
            "episode": "101", 
            "sequence": "S01", 
            "shot": "0010", 
            "step": "anm",
            "task": "blocking"}
        entity = 'task'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])


class TestSearchVersion(unittest.TestCase):

    # /////////////// #
    #     version     #
    # /////////////// #

    def test_find_version(self):
        payload = {
            "project": "PIPEV2", 
            "episode": "101", 
            "sequence": "S01", 
            "shot": "0010", 
            "step": "anm",
            "code": "blocking"}
        entity = 'version'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_version_in_step(self):
        payload = {
            "project": "PIPEV2", 
            "episode": "101", 
            "sequence": "S01", 
            "shot": "0010", 
            "step": "anm"}
        entity = 'version'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_version_asset(self):
        payload = {
            "project": "pipev2", 
            "asset": "charHolmA",
            "asset_type": "char",
            "variation": "default",
            "step": "look",
            "task": "default"}
        entity = 'version'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])


class TestSearchAssetShot(unittest.TestCase):

    # /////////////// #
    #    assetshot    #
    # /////////////// #

    def test_find_assetshotconnection(self):
        payload = {
            "project": "pnty",
            "episode": "104",
            "sequence": "S01",
            "shot": "0010"}
        entity = 'assetshotconnection'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_assetshot_asset(self):
        payload = {
            "project":"pnty",
            "type":"char",
            "asset":"charHolmA",
            "variation":"darkcircles"
        }
        entity = 'assetshotconnection'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])


class TestSearchAsset(unittest.TestCase):

    # /////////////// #
    #      asset      #
    # /////////////// #

    def test_find_asset(self):
        payload = {
            "project": "pipev2",
            "asset_type": "char",
            "asset": "charHolmA",
            "variation": "default"}
        entity = 'asset'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_asset_all_variation(self):
        payload = {
            "project": "pipev2",
            "asset_type": "char",
            "asset": "charHolmA"}
        entity = 'asset'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_asset_all_type(self):
        payload = { "project": "pipev2", "type": "char"}
        entity = 'asset'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])


class TestSearchPublishedFile(unittest.TestCase):

    # /////////////// #
    #  publishedfile  #
    # /////////////// #

    def test_find_publishedfile_shot(self):
        payload = {
            "project": "pipev2",
            "episode": "101",
            "sequence": "S01",
            "shot": "0010", 
            "step": "anm",
            "type": "abc"}
        entity = 'publishedFile'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_publishedfile_asset(self):
        payload = {
            "project": "pipev2",
            "asset_type": "char",
            "asset": "charHolmA",
            "variation": "default",
            "step": "look",
            "type": "tex" }
        entity = 'publishedFile'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_publishedfile_wrong_type(self):
        payload = {
            "project": "pipev2",
            "asset_type": "char",
            "asset": "charHolmA",
            "variation": "default",
            "step": "look",
            "type": "texxx" } # not data in publishedfile type
        entity = 'publishedFile'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertEqual(result['data'], [])


class TestSearchUser(unittest.TestCase):

    # /////////////// #
    #      user       #
    # /////////////// #

    def test_find_user(self):
        payload = {"user": "thaksaporn"}
        entity = 'user'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])


class TestSearchStep(unittest.TestCase):

    # /////////////// #
    #      step       #
    # /////////////// #

    def test_find_step(self):
        payload = {"step": "lay"}
        entity = 'step'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_wrong_step(self):
        payload = {"step": "lay_"}
        entity = 'step'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertEqual(result['data'], [])


class TestSearchDepartment(unittest.TestCase):

    # /////////////// #
    #   department    #
    # /////////////// #

    def test_find_department(self):
        payload = {"department": "pip"}
        entity = 'department'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_wrong_department(self):
        payload = {"department": "wip"}
        entity = 'department'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertEqual(result['data'], [])


class TestSearchStatus(unittest.TestCase):

    # /////////////// #
    #     status      #
    # /////////////// #

    def test_find_status(self):
        payload = {"status": "ip"}
        entity = 'status'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_wrong_status(self):
        payload = {"status": "aaa"}
        entity = 'status'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertEqual(result['data'], [])


class TestSearchThumbnail(unittest.TestCase):

    # /////////////// #
    #    thumbnail    #
    # /////////////// #

    def test_find_thumbnail_shot(self):
        payload = {
            "project":"pnty",
            "episode": "201",
            "entity": "shot" }
        entity = 'thumbnail'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

    def test_find_thumbnail_asset(self):
        payload = {
            "project":"pnty",
            "type": "char",
            "entity": "asset" }
        entity = 'thumbnail'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)
  
        self.assertNotEqual(result['data'], [])

class TestSearchNote(unittest.TestCase):

    # /////////////// #
    #      note       #
    # /////////////// #

    def test_find_note_shot(self):
        payload = {
            "project":"zeafrost",
            "episode": "101",
            "sequence": "S01",
            "shot": "0010"
        }
        entity = 'note'

        result = main_ctl.search(
            entity=entity.lower(),
            body=payload)

        self.assertNotEqual(result['data'], [])



if __name__ == '__main__':
    unittest.main()


