import unittest

from gooddataclient.connection import Connection
from gooddataclient.project import Project
from gooddataclient.dataset import Dataset, DateDimension
from gooddataclient.exceptions import DataSetNotFoundError,\
    ProjectNotOpenedError, ProjectNotFoundError

from tests.credentials import password, username
from tests import logger, examples


TEST_PROJECT_NAME = 'gdc_unittest'

class TestProject(unittest.TestCase):

    def setUp(self):
        self.connection = Connection(username, password, debug=0)
        #drop all the test projects:
        Project(self.connection).delete_projects_by_name(TEST_PROJECT_NAME)
        # you can delete here multiple directories from webdav
        for dir_name in ():
            self.connection.delete_webdav_dir(dir_name)

    def test_create_and_delete_project(self):
        project = Project(self.connection).create(TEST_PROJECT_NAME)
        self.assert_(project is not None)
        self.assert_(project.id is not None)
        project.delete()
        self.assertRaises(ProjectNotOpenedError, project.delete)
        self.assertRaises(ProjectNotFoundError, project.load, 
                          name=TEST_PROJECT_NAME)

    def test_create_structure(self):
        project = Project(self.connection).create(TEST_PROJECT_NAME)
        self.assertFalse(project.execute_maql('CREATE DATASET {dat'))
        dataset = Dataset(project)
        for example in examples.examples:
            self.assertRaises(DataSetNotFoundError, dataset.get_metadata,
                              name=example.schema_name)
            if hasattr(example, 'date_dimension'):
                self.assertFalse(project.execute_maql(example.maql), example.maql)
                DateDimension(project).create(name=example.date_dimension['name'],
                                                   include_time=('include_time' in example.date_dimension))
            self.assert_(project.execute_maql(example.maql), example.maql)
            self.assert_(dataset.get_metadata(name=example.schema_name))
        project.delete()

if __name__ == '__main__':
    unittest.main()
