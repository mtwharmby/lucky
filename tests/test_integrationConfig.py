'''
Created on 14 May 2016

@author: wnm24546
'''
from Lucky.IntegrationConfig import IntegrationConfig

from nose.tools import assert_true

class TestIntegrationConfig(object):
    
    def setUp(self):
        self.iConf = IntegrationConfig()
    
    def test_sanity_check(self):
        self.iConf.start = 200
        self.iConf.end = 900
        self.iConf.window = 300
        
        assert_true(self.iConf.checkConfig())
