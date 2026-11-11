# Source this file:  . scripts/env.sh
#
# It decides where the Python environment, the R library and the fetch cache
# of this checkout live, exports the result, and activates the Python
# environment when it exists.
#
# In the checkout (the default):
#   SPECFIRST_VENV    .venv              Python virtual environment
#   SPECFIRST_R_LIBS  .r-lib             R package library (also R_LIBS_USER)
#   fetch cache       third_party/cache  (or what third_party/cache-location names)
#
# Under SPECFIRST_HOME, when that variable is set or when the checkout is on
# a Windows drive under WSL (/mnt/<letter>/...), where the mount is slow and
# has no symbolic links. The default home is ~/.local/share/specfirst:
#   SPECFIRST_VENV    $SPECFIRST_HOME/venv-<checkout folder name>-<checksum of its path>
#   SPECFIRST_R_LIBS  $SPECFIRST_HOME/r-lib    shared by all checkouts
#   SPECFIRST_CACHE   $SPECFIRST_HOME/cache    shared by all checkouts

_sf_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Forget a cache location that an earlier run of this file chose for another checkout.
if [ -n "${_SPECFIRST_OWNS_CACHE:-}" ]; then
  unset SPECFIRST_CACHE _SPECFIRST_OWNS_CACHE
fi

_sf_home="${SPECFIRST_HOME:-}"
if [ -z "$_sf_home" ]; then
  case "$_sf_root" in
    /mnt/[a-z]/*)
      if grep -qi microsoft /proc/version 2>/dev/null; then
        _sf_home="${XDG_DATA_HOME:-$HOME/.local/share}/specfirst"
      fi
      ;;
  esac
fi

if [ -n "$_sf_home" ]; then
  # One environment per checkout: the folder name plus a checksum of its path,
  # so that two checkouts with the same folder name never share one.
  _sf_id="$(basename "$_sf_root")-$(printf '%s' "$_sf_root" | cksum | cut -d' ' -f1)"
  export SPECFIRST_VENV="$_sf_home/venv-$_sf_id"
  export SPECFIRST_R_LIBS="$_sf_home/r-lib"
  if [ -z "${SPECFIRST_CACHE:-}" ]; then
    export SPECFIRST_CACHE="$_sf_home/cache"
    export _SPECFIRST_OWNS_CACHE=1
  fi
else
  export SPECFIRST_VENV="$_sf_root/.venv"
  export SPECFIRST_R_LIBS="$_sf_root/.r-lib"
fi
# The R scripts in env/ read SPECFIRST_R_LIBS: R fills R_LIBS_USER with its
# own default when it is unset, so that variable cannot tell them where the
# project library is. R_LIBS_USER is set too, for interactive R sessions.
export R_LIBS_USER="$SPECFIRST_R_LIBS"

if [ -f "$SPECFIRST_VENV/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$SPECFIRST_VENV/bin/activate"
fi
unset _sf_root _sf_home _sf_id
