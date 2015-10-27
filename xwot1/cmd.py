__author__ = 'ruppena'

import sys
from xwot1.model2Python import Model2Python
from xwot1.model2WADL import Model2WADL
from xwot1.physical2virtualEntities import Physical2VirtualEntities

def p2v():
    """Entry point for the application script"""
    k = Physical2VirtualEntities()
    k.getArguments(sys.argv[1:])

def m2p():
    """Entry point for the application script"""
    k = Model2Python()
    k.getArguments(sys.argv[1:])

def m2w():
    """Entry point for the application script"""
    k = Model2WADL()
    k.getArguments(sys.argv[1:])