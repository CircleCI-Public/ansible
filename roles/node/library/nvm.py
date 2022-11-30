#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

def main():

    args = dict(
        versions=dict(type='list', elements='str', required=True),
        default=dict(type='str', required=False),
        npm=dict(type='list', elements='str', required=False)
    )

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=False
    )

    versions = module.params['versions']
    default = module.params['default']
    npm = module.params['npm']

    for version in versions:
        if version == 'lts':
            version = '--lts'
        elif version == 'current':
            version = 'node'
        if subprocess.run(['/bin/bash', '-i', '-c', 'source /home/circleci/.circlerc && nvm install ' + version]).returncode != 0:
            module.fail_json(msg='Failed to install NodeJS ' + version + '!')

    if default:
        if default == 'lts':
            if subprocess.run(['/bin/bash', '-i', '-c', 'source /home/circleci/.circlerc && nvm alias default lts/*']).returncode != 0:
                module.fail_json(msg='Failed to set nvm alias!')
        else:
            if subprocess.run(['/bin/bash', '-i', '-c', 'source /home/circleci/.circlerc && nvm alias default ' + default]).returncode != 0:
                module.fail_json(msg='Failed to set nvm alias!')
        if subprocess.run(['/bin/bash', '-i', '-c', 'source /home/circleci/.circlerc && nvm use default']).returncode != 0:
            module.fail_json(msg='Failed to set default NodeJS version!')

    if npm:
        for package in npm:
            if subprocess.run(['/bin/bash', '-lc', 'source /home/circleci/.circlerc && npm install -g ' + package]).returncode != 0:
                module.fail_json(msg='Failed to install ' + package + ' globally with npm!')

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
