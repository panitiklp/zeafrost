import argparse
import unittest

parser = argparse.ArgumentParser(description='Run unittest tests from multiple files.')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()

test_suite  = unittest.TestSuite()
test_loader = unittest.TestLoader()

test_files = [
    'test_project.Project.test_cache',
    'test_project.Project.test_create',
    'test_project.Project.test_created_directory_exists',
    'test_project.Project.test_search_by_name',
    'test_project.Project.test_search_by_id',
    'test_project.Project.test_update',

    'test_episode.Episode.test_cache',
    'test_episode.Episode.test_create',
    'test_episode.Episode.test_created_directory_exists',
    'test_episode.Episode.test_search_by_name',
    'test_episode.Episode.test_search_by_id',
    'test_episode.Episode.test_update',

    'test_sequence.Sequence.test_cache',
    'test_sequence.Sequence.test_create',
    'test_sequence.Sequence.test_created_directory_exists',
    'test_sequence.Sequence.test_search_by_name',
    'test_sequence.Sequence.test_search_by_id',
    'test_sequence.Sequence.test_update',

    'test_shot.Shot.test_cache',
    'test_shot.Shot.test_create',
    'test_shot.Shot.test_created_directory_exists',
    'test_shot.Shot.test_search_by_name',
    'test_shot.Shot.test_search_by_id',
    'test_shot.Shot.test_update',

    'test_asset.Asset.test_cache',
    'test_asset.Asset.test_create',
    'test_asset.Asset.test_created_directory_exists',
    'test_asset.Asset.test_search_by_name',
    'test_asset.Asset.test_search_by_id',
    'test_asset.Asset.test_update'
]

for test_file in test_files:
    _test = test_loader.loadTestsFromName(test_file)
    test_suite.addTests(_test)

verbosity = 1 if not args.verbose else 2

test_runner = unittest.TextTestRunner(verbosity=verbosity)
test_runner.run(test_suite)

