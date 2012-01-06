from tests.testImports import *
from controllers.cmsControllers import CMSLinksController
from models.BaseModels import Person

class TestLinks(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLinks, self).__init__(*args, **kwargs)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        
    def setUp(self):
        self.request = webapp.Request({
            "wsgi.input": StringIO(),
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/",
        })
        
        self.response = webapp.Response()
        self.link = CMSLinksController()
        self.link.Impersonated  = Person.CreateNew('test', 'test', 'test', 'test@test.com', 'test', True, True, 'local', None, False)        
        self.link.Impersonated.IsAdmin = True
        
    def tearDown(self):
        self.testbed.deactivate()
        
    def testIndexController(self):
        self.link.initialize(self.request, self.response)
        result = self.link.index('cms')
        self.assertIsNotNone(result, 'none is returned')
        print self.response.out.getvalue()
        self.assertTrue(isinstance(result, dict), "No Dict returned. Instead dict:\r\n")
