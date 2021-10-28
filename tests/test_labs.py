from util.utilities import Utilities
from laboratory.labs import Laboratory

class TestLabs():
    def test_fbc(self): 
        l = Laboratory([], {'gender': 'f', 'age': 84, 'anaemia': 1}, 0, [], Utilities({}))
        fbc = l.fbc()
        print(fbc)
        assert 'hb' in fbc