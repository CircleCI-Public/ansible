import os

class TestCCISpecific:
  def test_bashrc(self, host):
    file = host.file("/home/circleci/.bashrc")
    assert file.contains("source ~/.circlerc &>/dev/null") == True
    assert file.user == "circleci"
    assert file.group == "circleci"
    assert file.mode == 0o644

  def test_bin(self):
    assert os.path.exists("/home/circleci/bin")
    assert os.path.isdir("/home/circleci/bin")

  def test_ssh_config(self, host):
    sshConfig = host.file("/etc/ssh/ssh_config")
    assert sshConfig.contains("Host *") == True
    assert sshConfig.contains("StrictHostKeyChecking no") == True
    assert sshConfig.contains("HashKnownHosts no") == True

  def test_sshd_config(self, host):
    sshdConfig = host.file("/etc/ssh/sshd_config")
    assert sshdConfig.contains("UseDNS no") == True

  def test_xvfb(self, host):
    directory = host.file("/etc/systemd/system/xvfb.service")
    xvfbStarted = os.system("systemctl is-active xvfb.service")
    assert xvfbStarted == 0
    assert directory.mode == 0o644
