from tests.testImports import *

from lib.halicea.routes_helpers import get_controllers
from conf.settings import CONTROLLERS_DIR
 
t = get_controllers(CONTROLLERS_DIR)
print t