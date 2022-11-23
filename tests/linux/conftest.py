import pytest
import json
import os
import platform

@pytest.fixture
def manifest():
    return json.load(open('manifest/software.json'))

@pytest.fixture
def username():
    return os.environ.get('USER')

@pytest.fixture
def dotfile():
    if platform.system() == "Linux":
      return "/home/circleci/.circlerc"
    else:
      return "~/.bashrc"
