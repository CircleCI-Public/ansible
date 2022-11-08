import pytest
import subprocess
import os

def check_repositories(repo):
  directory = "/etc/apt/sources.list.d"
  dirList = os.listdir(directory)
  if any(repo in substring for substring in dirList):
    return 0
  else:
    return 1

@pytest.mark.parametrize("input, expected", [("chrome", 0), ("openjdk", 0), ("git_core", 0), ("mozillateam", 0)])
def test_repositories(input, expected):
  assert check_repositories(input) == expected

class TestBaseSettings:
  def test_timezone(self, host):
    timezone = host.file("/etc/timezone")
    assert timezone.contains("UTC")

  def test_apt_conf(self):
    confList = ['Assume-Yes "true"', '"--force-confnew"']

    for str in confList:
      if str in open("/etc/apt/apt.conf").read():
        check = 0
      else:
        check = 1
      assert check == 0

  def test_apt_conf_fail(self):
    with pytest.raises(Exception):
      confList = ['Assume-Yes "false"', '"--force-confold"']

      for str in confList:
        if str in open("/etc/apt/apt.conf").read():
          check = 0
        else:
          check = 1
        assert check == 0

  def test_noninteractive(self):
    debianFrontend = 'Defaults    env_keep += "DEBIAN_FRONTEND"'
    cmd = subprocess.run(['sudo', 'cat', '/etc/sudoers.d/env_keep'], capture_output=True)
    cmdCheck = cmd.stdout.decode("utf-8").split('\n', 1)[0]
    assert cmdCheck == debianFrontend
