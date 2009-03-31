from decorators import *

cuke = None

def getcuke():
    return cuke

@After
def _():
    global cuke
    
    cuke = None
