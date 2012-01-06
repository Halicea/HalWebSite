from tests.testImports import *
from controllers.cmsControllers import MenuController
import os
from models.cmsModels import Menu
class MenuControllerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MenuControllerTests, self).__init__(*args, **kwargs)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        
    def setUp(self):        
        self.menu = MenuController()
        self.req = webapp.Request({
            "wsgi.input": StringIO(),
            "wsgi.url_scheme":"http",
            "SERVER_NAME":'localhost',
            "SERVER_PORT":81,
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/",
        })
        self.resp = webapp.Response()
    def tearDown(self):
        #self.testbed.deactivate()
        pass

    def test_1_save(self):
        self.menu.initialize(self.req, self.resp)
        self.menu.params = DynamicParameters({'Name':'test_menu'})
        result = self.menu.save()
        result1 = Menu.all().fetch(10)
        self.assertEqual(len(result1), 1)
        self.assertEqual(result1[0].Name, 'test_menu')
        self.assertFalse(result.has_key('errors') and len(result['errors'])>0, str(result['errors']))

    def test_2_index(self):
        self.menu.initialize(self.req, self.resp)
        self.menu.params = DynamicParameters()
        result = self.menu.index()
        self.assertEqual(1, len(result['menus']), "One menu should exist in the datastore")
        if(len(result["menus"])<1):
            self.assertEqual("test_menu", result['menus'][0], "test_menu should be the only result in the menu list")
    
    def test_3_index_combo(self):
        self.menu.initialize(self.req, self.resp)
        self.menu.params = DynamicParameters()
        result = self.menu.index_combo()
        self.menu.respond(result)
        self.menu.response.out.getvalue()
