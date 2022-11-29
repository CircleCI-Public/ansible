import subprocess

class TestManifest:
  def test_ruby_versions(self, manifest):
    rbenv_versions = subprocess.run(['rbenv', 'versions'], capture_output=True).stdout.decode("utf-8")
    missing = ''
    for ruby in manifest['ruby']:
      if rbenv_versions.find(ruby) == -1:
        missing += f"{ruby} "
    assert missing == '', f"The following Ruby versions are missing: {missing}"

  def test_node(self, manifest, dotfile):
    missing = ''
    for node in manifest['node']:
      if node == 'lts':
          node_installed = subprocess.run(['/bin/bash', '-lc', 'source ' + dotfile + ' && nvm ls --no-colors | grep "lts/\\* ->"'], capture_output=True).stdout.decode("utf-8")
          if node_installed.find('N/A') != -1:
            missing += f"{node} "
      elif node == 'current':
          node_installed = subprocess.run(['/bin/bash', '-lc', 'source ' + dotfile + ' && nvm ls --no-colors | grep "node -> stable"'], capture_output=True).stdout.decode("utf-8")
          if node_installed.find('N/A') != -1:
            missing += f"{node} "
      else:
          node_installed = subprocess.run(['/bin/bash', '-lc', 'source ' + dotfile + ' && nvm ls --no-colors | grep -Em 1 "\\->"'], capture_output=True).stdout.decode("utf-8")
          if node_installed.find(node) == -1:
            missing += f"{node} "
    assert missing == '', f"The following NodeJS versions are missing: {missing}"

  def test_default_node(self, manifest, dotfile):
    node_default = subprocess.run(['/bin/bash', '-lc', 'source ' + dotfile + ' && nvm ls --no-colors | grep "default ->"'], capture_output=True).stdout.decode("utf-8")
    assert node_default.find(manifest['defaults']['node']) != -1, f"The default NodeJS should be {manifest['defaults']['node']} but found {node_default}!"

  def test_npm_packages(self, manifest):
    npm = subprocess.run(['npm', 'list', '-g'], capture_output=True).stdout.decode("utf-8")
    missing = ''
    for globalPackages in manifest['npm']:
      if npm.find(globalPackages) == -1:
        missing += f"{globalPackages} "
    assert missing == '', f"The following global npm packages are missing: {globalPackages}"

  def test_python_interpreter(self):
    python_interpreter = subprocess.run(['which', 'python3'], capture_output=True).stdout.decode("utf-8")
    missing = ''
    if python_interpreter.find(".pyenv") == -1:
      missing = f"{python_interpreter}"
    assert missing == '', f"The python interpreter is missing or is not correctly set to: {python_interpreter}"

  def test_python(self, manifest):
      installed_pythons = subprocess.run(['pyenv', 'versions'], capture_output=True).stdout.decode("utf-8")
      missing = ''
      for python in manifest['python']:
          if installed_pythons.find(python) == -1:
              missing += f"{python}"
      assert missing == '', f"The following Python versions are missing: {missing}"

  def test_default_python(self, manifest):
      python_default = subprocess.run(['python3', '--version'], capture_output=True).stdout.decode("utf-8")
      assert python_default.find(manifest['defaults']['python']) != -1, f"The default Python should be {manifest['defaults']['python']} but found {python_default}!"
