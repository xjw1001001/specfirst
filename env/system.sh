#!/usr/bin/env bash
# Install the system packages on Ubuntu 24.04. Run once per machine, as root:
#
#   sudo bash env/system.sh
#
# From Windows, for a WSL distribution:
#
#   wsl -d Ubuntu-24.04 -u root -- bash /mnt/<drive>/<path>/env/system.sh
#
# R comes from CRAN's own repository for Ubuntu, at the exact version in
# env/r-version.txt. Ubuntu 24.04 ships R 4.3.3, which current CRAN packages
# no longer support (docs/lessons.md, lesson 7).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DEBIAN_FRONTEND=noninteractive

apt-get update
# shellcheck disable=SC2046
apt-get install -y --no-install-recommends $(grep -v '^#' "$here/apt-packages.txt")

# CRAN's signing key (Michael Rutter), checked by fingerprint before use.
key=/etc/apt/keyrings/cran_ubuntu_key.asc
fingerprint=E298A3A825C0D65DFD57CBB651716619E084DAB9
install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc -o "$key.new"
if ! gpg --show-keys --with-colons "$key.new" | grep -q "^fpr:.*:$fingerprint:"; then
  echo "the CRAN signing key does not have the expected fingerprint" >&2
  rm -f "$key.new"
  exit 1
fi
mv "$key.new" "$key"
echo "deb [signed-by=$key] https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/" \
  > /etc/apt/sources.list.d/cran.list
apt-get update

r="$(grep -v '^#' "$here/r-version.txt" | head -n 1)"
apt-get install -y --no-install-recommends --allow-downgrades \
  "r-base-core=$r" "r-base=$r" "r-base-dev=$r" "r-recommended=$r"
# The recommended R packages (r-cran-matrix and the like) must be the builds
# for this R, also on a machine that had Ubuntu's older ones installed.
# shellcheck disable=SC2046
apt-get install -y --no-install-recommends \
  $(dpkg-query -W -f='${db:Status-Abbrev}${Package}\n' 'r-cran-*' | sed -n 's/^ii //p')
R --version | head -n 1
