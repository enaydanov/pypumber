from decorators import *

@Given(r"I'm a cucumber$")
def _():
   print '.'
   pending()

@Given(r'failing')
def _():
   1 / 0

@Given(r'passing')
def _():
  print '.'
 
@Before
def _():
   print 'before'
 
@After
def _():
   print 'after'
