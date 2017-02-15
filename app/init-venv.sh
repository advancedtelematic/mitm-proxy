#!/bin/bash
set -e
set -o pipefail

# Creates a venv, installs packages

echo_bold() {
  echo -e "\033[1;37m$@\033[0m"
}

declare -r script_dir=$(readlink -f $(dirname $0))
cd "$script_dir"

if ! hash virtualenv 2> /dev/null; then
  echo_bold 'Installing virtualenv with pip'
  pip install virtualenv
fi

declare -r venv_dir='venv'
declare -r python_version='python3'
declare -r python_bin="$(which "$python_version")"

if [ -z "$python_bin" ]; then
  echo "Unable to locate Python executable '$python_version'. PATH: $PATH" >&2
  exit 1
fi

echo_bold 'Setting up virtualenv'

if [ ! -f "$venv_dir/bin/activate" ]; then
  rm -rf "$venv_dir"
  virtualenv -p "$python_bin" "$venv_dir"
fi

source "$venv_dir/bin/activate"

pip install -r <(cat requirements/*.txt)

echo_bold 'Success'
if [ -t 1 ]; then
  echo_bold "To enable the virtualenv, run \`source $script_dir/$venv_dir/bin/activate\`"
  echo_bold 'Remember: You need to do this for every terminal session!'
  echo_bold 'To disable the virtualenv, run `deactivate`'
fi
