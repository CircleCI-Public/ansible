class TestUser:
  def test_username(self, host, username):
    user = host.user(username)
    user_groups = user.groups

    if username == 'circleci':
        expected_uid = 1001
    else:
        expected_uid = 1

    assert user.uid == expected_uid
    assert user.gid == 1002
    assert "google-sudoers" in user_groups

  def test_passwordless_sudo(self, host):
    cmd = host.run('sudo -n true')
    assert cmd.rc == 0