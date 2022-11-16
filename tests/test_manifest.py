import subprocess
import os

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
  
  def test_npm_local_packages(self, manifest):
    npmLocal = subprocess.run(['npm', 'list'], capture_output=True).stdout.decode("utf-8")
    missing = ''
    for localPackages in manifest['npmLocal']:
      if npmLocal.find(localPackages) == -1:
        missing += f"{localPackages} "
    assert missing == '', f"The following local npm packages are missing: {localPackages}"
        
  def test_npm_global_packages(self, manifest):
    npmGlobal = subprocess.run(['npm', 'list', '-g'], capture_output=True).stdout.decode("utf-8")
    missing = ''
    for globalPackages in manifest['npmGlobal']:
      if npmGlobal.find(globalPackages) == -1:
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

  def test_go(self, manifest):
    go_version = subprocess.run(['go', 'version'], capture_output=True).stdout.decode("utf-8")
    assert go_version.find(manifest['defaults']['go']) != -1, f"Go was not found or the version is incorrect. Output: {go_version}"

  def test_gradle(self, manifest):
    gradle = subprocess.run(['gradle', '--version'], capture_output=True).stdout.decode("utf-8")
    assert gradle.find(manifest['gradle']) != -1, f"Gradle was not found or the version is incorrect. Output: {gradle}"

  def test_maven(self, manifest):
    maven = subprocess.run(['mvn', '--version'], capture_output=True).stdout.decode("utf-8")
    assert maven.find(manifest['maven']) != -1, f"Maven was not found or the version is incorrect. Output: {maven}"

  def test_clojure(self, manifest):
    lein = subprocess.run(['lein', '--version'], capture_output=True).stdout.decode("utf-8")
    assert lein.find(manifest['lein']) != -1, f"Lein was not found or the version is incorrect. Output: {lein}"

  def test_awscli(self, manifest):
    aws = subprocess.run(['aws', '--version'], capture_output=True).stdout.decode("utf-8")
    assert aws.find(manifest['aws-cli']) != -1, f"aws-cli was not found or the version is incorrect. Output: {aws}"

  def test_docker(self, manifest):
    for package in manifest['docker']:
      missing = ''
      version = subprocess.run([package, '--version'], capture_output=True).stdout.decode("utf-8")
      if version.find(package) == -1:
        missing += f"{package}"
    assert missing == '', f"The following packages for Docker are missing: {missing}"

  def test_gcloud(self, manifest):
    gcloud  = subprocess.run(['gcloud', '--version'], capture_output=True).stdout.decode("utf-8")
    assert gcloud.find(manifest['gcloud']) != -1, f"gcloud was not found or the version is incorrect. Output: {gcloud}"

  def test_chrome(self):
    chrome = subprocess.run(['google-chrome', '--version'], capture_output=True)
    assert chrome.returncode != -1, f"Chrome was not found. Output: {chrome}"

  def test_firefox(self):
    firefox = subprocess.run(['firefox', '--version'], capture_output=True)
    assert firefox.returncode != -1, f"Firefox was not found. Output: {firefox}"

  def test_scala(self, manifest):
    sbt = subprocess.run(['sbt', '-V'], capture_output=True).stdout.decode("utf-8")
    assert sbt.find(manifest['defaults']['sbt']) != -1, f"sbt/scala was not found or the version is incorrect. Output: {sbt}"

  def test_default_java(self, manifest):
    java = subprocess.run(['java', '--version'], capture_output=True).stdout.decode("utf-8")
    assert java.find(manifest['defaults']['java']) != -1, f"The default version of Java was not found or is incorrect. Output: {java}"

  def test_java_versions(self, manifest):
    missing = ''
    for version in manifest['java']:
        path = "/usr/lib/jvm/java-{version}-openjdk-{machine_arch}/bin/java"
        if os.path.exists(path) == -1:
          missing += f"{version}"
    assert missing == '', f"Java was not found or is missing. Output: {missing}"

  def test_yq(self, manifest):
    yq = subprocess.run(['yq', '--version'], capture_output=True).stdout.decode("utf-8")
    assert yq.find(manifest['defaults']['yq']) != -1, f"yq was not found or the version is incorrect. Output: {yq}"
