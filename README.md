# ansible

Ansible playbooks and roles that CircleCI uses to provision the VM images
backing the [machine executor][machine-executor] (and related image types such
as Remote Docker and Android). The playbooks are driven by [Packer][packer]
against a cloud provider (today: Google Compute Engine, with a Vultr plugin
also wired up) and produce the public CircleCI machine images that customer
jobs run on.

This repo is published publicly so that customers can see exactly what is
installed on the machines that execute their jobs, reproduce equivalent
environments locally if needed, and audit the provisioning steps.

[machine-executor]: https://circleci.com/docs/configuration-reference/#machine-executor-linux-windows-and-macos
[packer]: https://developer.hashicorp.com/packer

## How it fits together

```
            +-----------------------------+
            |   .circleci/config.yml      |
            |   (quarterly / canary /     |
            |    test workflows)          |
            +--------------+--------------+
                           |
                           v
            +-----------------------------+
            |   packer/packer.pkr.hcl     |
            |   sources:                  |
            |     - googlecompute         |
            |     - vultr (plugin pinned) |
            +--------------+--------------+
                           |
                           |  provisioner "ansible"
                           v
            +-----------------------------+
            |   Top-level playbooks       |
            |     linux-playbook.yml      |
            |     android-playbook.yml    |
            |     remote_docker-...yml    |
            |     windows-playbook.yml    |
            |     windows-nvidia-...yml   |
            +--------------+--------------+
                           |
                           |  roles + manifest/*.json
                           v
            +-----------------------------+
            |   roles/<name>/             |
            |   (common, docker, node,    |
            |    python3, java, ...)      |
            |   roles/windows/<name>/     |
            +-----------------------------+
```

Packer boots a fresh base VM in the cloud (e.g. an Ubuntu 22.04 image on GCE),
runs the selected playbook against it over SSH/WinRM, and then snapshots the
disk to produce a versioned CircleCI machine image.

## Repository layout

| Path | Purpose |
| --- | --- |
| `linux-playbook.yml` | Production Linux machine executor image (Ubuntu). Installs the full software stack: Node, Java, Python, Ruby, Chrome, Docker, Go, Clojure, Scala, AWS/GCloud CLIs, sysadmin/dev tools, Syft, etc. |
| `linux-playbook-test.yml` | Stripped-down playbook used by the `build-test` CI workflow to smoke-test changes against a real VM without baking a full image. |
| `android-playbook.yml` | Linux base + Android SDK / NDK / build tools, used to build the Android machine executor image. |
| `remote_docker-playbook.yml` | Minimal Linux + Docker host used as the Remote Docker image. |
| `windows-playbook.yml` | Windows Server image (Server 2019/2022). Runs the `windows/*` roles via WinRM. |
| `windows-nvidia-playbook.yml` | Same as `windows-playbook.yml` plus the `windows/nvidia` role for GPU executors. |
| `packer/packer.pkr.hcl` | Packer build definition (GCE source today, with the Vultr plugin declared as a `required_plugin`). Wires Packer's `ansible` provisioner to the selected playbook. |
| `packer/variables.pkr.hcl` | Packer input variables (image name/family, source image, GCP project, zone, ssh user, playbook file, etc.). |
| `group_vars/linux_configure_vars.yml` | Shared Ansible variables for Linux runs (`circleci_user`, `circleci_home`, remote tmp dir). |
| `group_vars/windows_configure_vars.yml` | WinRM connection settings for Windows runs. |
| `manifest/software.json` | Pinned software versions for the Linux image (Ruby, Node, Python, Docker, Go, Maven, Gradle, gcloud, etc.). Treated as the source of truth for what gets installed. |
| `manifest/android-test.json` | Pinned versions and Android SDK platforms / build-tools / NDK / CMake for the Android image. |
| `manifest/docker23.json`, `docker24.json` | Docker / containerd / compose pins used for the Remote Docker image variants. |
| `manifest/windows-software.json`, `windows2019-software.json`, `windows2022-software.json` | Pinned versions for the Windows image families. |
| `roles/<name>/` | Linux roles, organised by the software they install (e.g. `common`, `docker`, `node`, `python3`, `java`, `ruby`, `chrome`, `golang`, `gcloud`, `awscli`, `syft`, `dpkg_configure`, ...). |
| `roles/windows/<name>/` | Windows-specific roles (`common`, `create_users`, `install_cloudtools`, `devtools`, `microsoft_tools`, `nvidia`, `syft`, `windows_updates`, `disable_services`, `buildagent_prereq`). |
| `tests/linux/` | `pytest` + `testinfra` checks that compare the installed software on a built image against `manifest/software.json` (Ruby/Node/Python versions, npm globals, base settings, repos). |
| `.circleci/config.yml` | CI pipelines that build images on GCP via Packer + Ansible. |
| `.github/CODEOWNERS` | Ownership: `@CircleCI-Public/images`. |
| `LICENSE` | MIT. |

## The `common` role (run by every Linux playbook)

`roles/common/tasks/main.yml` orchestrates three sub-task files that every
Linux image relies on:

1. `system_prep.yml` — registers the machine architecture, ensures the
   `circleci` user (uid 1001) and `aws-sudoers` group exist with passwordless
   sudo, fixes ownership of `~circleci/.ssh`, and resets the connection so the
   new groups take effect. Has provider-specific guards (e.g. for Vultr's
   Ubuntu 26.04 image that ships without `ubuntu`/`netdev` groups, and to skip
   `rlimit_core` on 26.04).
2. `base.yml` — purges `snapd`, sets the timezone to UTC, enables the
   `universe` and `git-core` repositories (skipping `git-core` on 24.04+),
   installs core packages (`build-essential`, `cmake`, `curl`, `git`, `make`,
   `ffmpeg`, `imagemagick`, `mercurial`, …), installs cloud-vendor extra
   kernel modules (`linux-modules-extra-aws` for AWS/Vultr,
   `linux-modules-extra-gcp` otherwise — both ignore failures on 26.04), and
   raises the open-files ulimit to 65536.
3. `cci_specific.yml` — writes the `circleci` user's shell setup
   (`.bash_profile`, `.bashrc`, `.circlerc` with `GIT_ASKPASS`, `SSH_ASKPASS`,
   `DISPLAY=:99`, etc.), hardens `sshd` (`PasswordAuthentication no`,
   `MaxStartups 1000`, `MaxSessions 1000`, `PermitTunnel yes`,
   `AddressFamily inet`), installs and enables `xvfb` on display `:99` so
   Selenium/headless-browser tests work out of the box, and installs
   `iptables-persistent`.

Most of the contract that downstream language roles rely on — the `circleci`
user, `/home/circleci`, `.circlerc`, the `/opt/circleci` install root — comes
from this role.

## Build pipelines (`.circleci/config.yml`)

The repo's own CircleCI config defines three workflows; only one runs per
pipeline based on parameters and branch name:

- **`build-quarterly`** (`pipeline.parameters.build_quarterly: true`, branches
  matching `build*`): full quarterly base image build against Ubuntu 22.04
  Jammy, using `manifest/software.json` and `linux-playbook.yml`. Publishes to
  GCP image family `ansible-ubuntu-2204-base`.
- **`build-canary`** (`pipeline.parameters.build_canary: true`, branches
  matching `canary*`): canary builds on top of the most recent base image
  (`source_image_family: ansible-ubuntu-2204-canary`).
- **`build-test`** (any branch starting with `test*`, `refactor*`, `fix*`, or
  `feat*`): runs `linux-playbook-test.yml` against a Jammy VM with
  `skip_create_image: true` so it exercises the change end-to-end without
  publishing an image.

The `build_gcp` job:

1. Generates a GCP credential file from `${CCI_GCE_B64_CREDENTIALS}`.
2. Installs the `gcloud` CLI (beta) and authenticates.
3. Writes `PKR_VAR_*` environment variables for every Packer variable.
4. Runs `packer init` and `packer build -only=googlecompute.gcp-canary-base
   packer/`.
5. Persists `packer_vars`, the build URL and the manifest to the workspace
   and uploads them as artifacts.

The custom `check_source_paths` command halts the job early when the branch
hasn't actually modified the manifest under `source_dirs`, unless `run_build`
is set to `true` (used for force-rebuilds, e.g. for patch releases).

## Manifests are the source of truth

Each manifest file in `manifest/` is loaded by Packer as
`--extra-vars @manifest/software.json` (see `packer/packer.pkr.hcl`) and
becomes top-level Ansible variables that roles consume. For example:

- `roles/docker/tasks/main.yml` installs `docker-ce={{ docker_version }}`,
  `containerd.io={{ containerd_version }}`,
  `docker-compose-plugin={{ docker_compose_version }}`.
- `roles/python3` clones `pyenv` at tag `v{{ pyenv_version }}` and installs
  each version from `python_versions`.
- `roles/node` installs every entry of `node` via `nvm` and sets
  `{{ nodelts_version }}` as the default.
- `roles/syft` calls `sbom generate "{{ image_name }}" "{{ image_tag }}"` to
  record an SBOM for the resulting image.

To bump a piece of software, edit the relevant manifest JSON and open a PR.
The CI `build-test` workflow will smoke-test the change; quarterly/canary
builds publish the image.

## Building an image locally

You usually do not need to do this — the CircleCI pipelines build the
official images — but it's useful for debugging a role.

Prerequisites:

- Packer >= 1.8 (HCL2)
- Ansible
- A GCP service-account JSON key with permission to create images in the
  target project, or credentials for whichever Packer source you wire up
- For the Vultr source: a Vultr API key

```bash
packer init packer/

export PKR_VAR_account_file=/path/to/service-account.json
export PKR_VAR_project_id=my-gcp-project
export PKR_VAR_zone=us-east1-c
export PKR_VAR_ssh_username=circleci
export PKR_VAR_source_image_family=ubuntu-2204-lts
export PKR_VAR_image_name=ansible-ubuntu-2204-dev
export PKR_VAR_image_family=ansible-ubuntu-2204-dev
export PKR_VAR_skip_create_image=true              # debug-only run
export PKR_VAR_playbook_file=./linux-playbook.yml  # or another playbook

packer build -only=googlecompute.gcp-canary-base packer/
```

The Packer `ansible` provisioner already passes
`--extra-vars @manifest/software.json` and the SSH options required by GCE.

## Tests

`tests/linux/` is a small `pytest` suite that runs **on a freshly built image**
(via `testinfra`) and asserts that the runtime state matches the manifest:

- `test_manifest.py` — every Ruby version in the manifest is present in
  `rbenv versions`, every Node version is present in `nvm ls`, the default
  Node/Python match `manifest.defaults`, every global npm package and pip
  package is installed, and `python3` resolves to the `pyenv` shim.
- `test_base_role.py` — APT repositories for `chrome`, `openjdk`, `git_core`,
  `mozillateam` are present, `/etc/timezone` contains `UTC`, `/etc/apt/apt.conf`
  contains `Assume-Yes "true"` and `--force-confnew`, and
  `Defaults env_keep += "DEBIAN_FRONTEND"` is in `/etc/sudoers.d/env_keep`.
- `test_system_prep.py` — checks the `circleci` user / group / sudoers setup
  applied by `roles/common/tasks/system_prep.yml`.
- `conftest.py` — loads `manifest/software.json` and resolves the right
  per-OS dotfile (`/home/circleci/.circlerc` on Linux, `~/.bashrc` elsewhere).

These are not run by `.circleci/config.yml` in this repo; they are intended to
be executed against a built image (typically from the downstream image-build
pipeline that consumes these playbooks).

## Conventions

- All Linux tasks run as the build user and `become: true` where root is
  required, so they work against any cloud base image that ships with a
  default user that has passwordless sudo.
- The provisioning contract is: a `circleci` user (uid `1001`) with home
  `/home/circleci`, passwordless sudo, and `/opt/circleci` as the package
  install root. Roles like `python3` (`/opt/circleci/.pyenv`) and `node`
  (`/opt/circleci/.nvm`) install there so the runtime is owned by the
  `circleci` user rather than root.
- Per-language shell configuration is appended to
  `/home/circleci/.circlerc` between marker pairs (`PYTHON START`/
  `PYTHON END`, `NODE START`/`NODE END`, …) using `blockinfile`, so re-runs
  are idempotent.
- Windows roles use `ansible.windows` / `chocolatey.chocolatey` collections
  and connect over WinRM (`group_vars/windows_configure_vars.yml`).

## License

[MIT](./LICENSE). Copyright © 2021 – 2023 CircleCI.

Ownership: `@CircleCI-Public/images` (see `.github/CODEOWNERS`).
