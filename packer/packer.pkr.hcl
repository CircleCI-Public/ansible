packer {
  required_plugins {
    ansible = {
      # this version contains a fix for the SSH extra arguments quoting issues
      version = ">= 1.1.1"
      source  = "github.com/hashicorp/ansible"
    }
  }
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "googlecompute" "gcp-canary-base" {
  account_file        = var.account_file
  disk_size           = 14
  image_family        = var.image_family
  image_name          = "${var.image_name}-${local.timestamp}"
  project_id          = var.project_id
  source_image        = var.source_image
  source_image_family = var.source_image_family
  ssh_username        = var.ssh_username
  zone                = var.zone
  skip_create_image   = var.skip_create_image
}

build {
  sources = ["source.googlecompute.gcp-canary-base"]

  provisioner "ansible" {
    ansible_env_vars = ["ANSIBLE_HOST_KEY_CHECKING=False", "ANSIBLE_SSH_ARGS=-o ForwardAgent=yes -o ControlMaster=auto -o ControlPersist=60s -o PubkeyAcceptedKeyTypes=+ssh-rsa -o HostKeyAlgorithms=+ssh-rsa"]
    extra_arguments  = ["-vvv", "--extra-vars", "@manifest/software.json", "--scp-extra-args", "'-O'"]
    playbook_file    = var.playbook_file
  }

  provisioner "shell" {
    inline = ["sudo rm -rf /opt/circleci-provision-scripts/", "sudo rm -rf .ansible ansible"]
  }

  provisioner "shell" {
    inline = ["set -ex\n\n# disable autoupdates on boot\n# these can disturb and slow boot behavior\n# and we aim to finalize image\nsudo sed -i -e '/APT::Periodic::Update-Package-Lists/g' /etc/apt/apt.conf.d/10periodic\necho 'APT::Periodic::Unattended-Upgrade \"0\";' | sudo tee -a /etc/apt/apt.conf.d/10periodic\nsudo rm -rf ~/.ssh/authorized_keys /home/circleci/.ssh/authorized_keys /tmp/circleci-provisioner\n\n# Check that circleci can sudo with no password\nsudo -u circleci -- sudo --askpass --validate\n\necho yay it finished\n"]
  }
}
