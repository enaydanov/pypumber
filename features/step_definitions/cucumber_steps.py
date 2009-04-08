from decorators import *
from os.path import normpath, dirname, join
from subprocess import Popen, PIPE, STDOUT
from difflib import Differ
import re

PYTHON='pythonw'
PYTHON_OPTIONS='-u'
PYPUMBER_COMMAND = normpath(join(dirname(__file__), '..', '..', 'pypumber.py'))

@Given(r'^I am in (.*)$')
def _(dir):
   world.dir = dir

@When(r'^I run cucumber (.*)$')
def _(cmd):
    if 'dir' not in world:
        world.dir = 'self_test'
    
    cwd = normpath(join(dirname(__file__), '..', '..', 'examples', world.dir.value()))
    command = '%s %s %s %s' % (PYTHON, PYTHON_OPTIONS, PYPUMBER_COMMAND, cmd)
    exe = Popen(command, cwd=cwd, stdout=PIPE, stderr=STDOUT)
    world.out = exe.communicate()[0]
    world.status = exe.returncode

@Then(r'^it should (fail|pass) with$', output=multi)
def _(success, output):
    d = Differ()
    assert world.out.value() == output, '\n' + '\n'.join(d.compare(world.out.value().split('\n'), output.split('\n')))
    if success == 'fail':
        assert world.status.value() != 0
    else:
        assert world.status.value() == 0

@Then(r'^the output should contain$', text=multi)
def _(text):
    assert world.out.value().find(text) != -1

@Then(r'^"(.*)" should contain$', text=multi)
def _(filename, text):
    assert open(filename).read() == text

@Then(r'/^"(.*)" should match$', text=multi)
def _(filename, text):
    assert re.search(text, open(filename).read())
