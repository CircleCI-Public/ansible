#!/usr/bin/python

import subprocess
from ansible.module_utils.basic import AnsibleModule

def main():

    args = dict(
        versions=dict(type='list', elements='str', required=True),
        default=dict(type='str', required=False)
    )

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=False
    )

    versions = module.params['versions']
    default = module.params['default']
    
    for version in versions:
        output = subprocess.run(['/bin/bash', '-lc', 'source /home/circleci/.circlerc && pyenv install ' + version])
        if output.returncode != 0:
            module.fail_json(msg='Problem installing Python ' + version + output.stdout + output.stderr)

    if default:
        output = subprocess.run(['/bin/bash', '-lc', 'source /home/circleci/.circlerc && pyenv global ' + default])
        if output.returncode != 0:
            module.fail_json(msg='Problem setting default Python')

    subprocess.run(['/bin/bash', '-lc', 'source /home/circleci/.circlerc && pyenv rehash'])

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()