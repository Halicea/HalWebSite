from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from lib.halicea.decorators import *
#{%block imports%}
#{%endblock%}
################################

class WelcomeController(hrh):
    @ClearDefaults()
    @Default('UnderConstruction')
    def SetOperations(self): pass
    def welcome(self):
        return {}
    
    def UnderConstruction(self, *args):
        return {}