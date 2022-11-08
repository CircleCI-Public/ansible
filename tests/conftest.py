import pytest
import json
import os

@pytest.fixture
def manifest():
    return json.load(open('manifest/software.json'))

@pytest.fixture
def username():
    return os.environ.get('USER')
