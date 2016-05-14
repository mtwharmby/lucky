'''
Created on 14 May 2016

@author: wnm24546
'''
from Lucky.IntegrationConfig import IntegrationConfig
from Lucky.Exceptions import LuckyConfigException

from nose.tools import assert_true
from nose.tools import assert_raises

class TestIntegrationConfig(object):
    
    def setUp(self):
        self.iConf = IntegrationConfig()
    
    def test_sanity_check(self):
        self.iConf.start = 200
        self.iConf.end = 900
        self.iConf.window = 300
        
        assert_true(self.iConf.checkConfig())

    def test_end_lessthan_start(self):
        self.iConf.start = 900
        self.iConf.end = 200
        self.iConf.window = 300
        
        assert_raises(LuckyConfigException, self.iConf.checkConfig)
