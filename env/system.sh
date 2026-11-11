#!/usr/bin/env bash
# Install the system packages of env/apt-packages.txt on Ubuntu 24.04.
# Run once per machine, as root:
#
#   sudo bash env/system.sh
#
# From Windows, for a WSL distribution:
#
#   wsl -d Ubuntu-24.04 -u root -- bash /mnt/<drive>/<path>/env/system.sh
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DEBIAN_FRONTEND=noninteractive
apt-get update
# shellcheck disable=SC2046
apt-get install -y --no-install-recommends $(grep -v '^#' "$here/apt-packages.txt")
