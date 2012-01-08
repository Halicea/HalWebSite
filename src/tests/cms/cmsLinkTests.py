from tests.testImports import *
from controllers.cmsControllers import CMSLinksController
from models.BaseModels import Person

class TestLinks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testbed = testbed.Testbed()
        cls.testbed.activate()
        cls.testbed.init_datastore_v3_stub()
        cls.testbed.init_memcache_stub()

    @classmethod
    def tearDownClass(cls):
        cls.testbed.deactivate()
        
    def setUp(self):
        self.request = webapp.Request({
            "wsgi.input": StringIO(),
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/",
        })
        self.response = webapp.Response()
        self.link = CMSLinksController()
        #Impersonate the login
        self.link.Impersonated  = Person.CreateNew('test', 'test', 'test', 'test@test.com', 'test', True, True, 'local', None, False)        
        #set Admin
        self.link.Impersonated.IsAdmin = True

    def testIndexController(self):
        self.link.initialize(self.request, self.response)
        result = self.link.index('cms')
        self.assertIsNotNone(result, 'none is returned')
        print self.response.out.getvalue()
        self.assertTrue(isinstance(result, dict), "No Dict returned. Instead dict:\r\n")
    