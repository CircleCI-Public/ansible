import pytest
import subprocess
import os

def check_repositories(repo):
  dirList = os.listdir("/etc/apt/sources.list.d")
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
    assert timezone.contains("UTC") == True

  def test_apt_conf(self):
    confList = ['Assume-Yes "true"', '"--force-confnew"']
    missing = ''
    for str in confList:
      if str not in open("/etc/apt/apt.conf").read():
        missing += f"{str} "
    assert missing == '', f"Missing the following additions to apt.conf: {missing}"

  def test_apt_conf_fail(self):
    with pytest.raises(Exception):
      confList = ['Assume-Yes "false"', '"--force-confold"']
      missing = ''
      for str in confList:
        if str not in open("/etc/apt/apt.conf").read():
          missing += f"{str} "
      assert missing == '', f"Intentionally missing the following additions in apt.conf: {missing}"

  def test_noninteractive(self):
    debianFrontend = 'Defaults    env_keep += "DEBIAN_FRONTEND"'
    cmd = subprocess.run(['sudo', 'cat', '/etc/sudoers.d/env_keep'], capture_output=True)
    cmdCheck = cmd.stdout.decode("utf-8").split('\n', 1)[0]
    assert cmdCheck == debianFrontend, f"{debianFrontend} is missing from the sudoers configuration"
