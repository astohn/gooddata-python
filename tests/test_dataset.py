import unittest

from gooddataclient.project import Project
from gooddataclient.connection import Connection
from gooddataclient.dataset import Dataset, DateDimension

from tests.credentials import password, username
from tests.test_project import TEST_PROJECT_NAME
from tests import logger, examples

class TestDataset(unittest.TestCase):

    def setUp(self):
        self.connection = Connection(username, password, debug=0)
        #drop all the test projects:
        Project(self.connection).delete_projects_by_name(TEST_PROJECT_NAME)
        self.project = Project(self.connection).create(TEST_PROJECT_NAME)

    def tearDown(self):
        self.project.delete()

    def test_create_date_dimension(self):
        for example in examples.examples:
            if hasattr(example, 'date_dimension'):
                DateDimension(self.project).create(name=example.date_dimension['name'],
                               include_time=('include_time' in example.date_dimension))
                # TODO: verify the creation

    def test_upload_dataset(self):
        for example in examples.examples:
            if hasattr(example, 'date_dimension'):
                DateDimension(self.project).create(name=example.date_dimension['name'],
                                                   include_time=('include_time' in example.date_dimension))

            dataset = Dataset(self.project)
            dataset.upload(example.maql, example.data_csv, example.sli_manifest)
            dataset_metadata = dataset.get_metadata(name=example.schema_name)
            self.assert_(dataset_metadata['dataUploads'])
            self.assertEquals('OK', dataset_metadata['lastUpload']['dataUploadShort']['status'])

    def test_date_maql(self):
        date_dimension = DateDimension(self.project)
        self.assertEquals('INCLUDE TEMPLATE "URN:GOODDATA:DATE"', date_dimension.get_maql())
        self.assertEquals('INCLUDE TEMPLATE "URN:GOODDATA:DATE" MODIFY (IDENTIFIER "test", TITLE "Test");\n\n',
                          date_dimension.get_maql('Test'))
        self.assertEquals(examples.forex.date_dimension_maql, date_dimension.get_maql('Forex', include_time=True))
        self.assertEquals(examples.forex.date_dimension_maql.replace('forex', 'xerof').replace('Forex', 'Xerof'), 
                          date_dimension.get_maql('Xerof', include_time=True))


if __name__ == '__main__':
    unittest.main()
