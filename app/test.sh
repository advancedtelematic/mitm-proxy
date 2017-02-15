#!/usr/bin/env bash
set -eo pipefail

# Runs the test suite and builds test reports

echo_bold() {
  echo -e "\033[1;37m$@\033[0m"
}

declare -r script_dir="$(readlink -f $(dirname $0))"
cd "$script_dir"

if [ ! -f 'venv/bin/activate' ]; then
  ./init-venv.sh
fi

source 'venv/bin/activate'
coverage erase
coverage run ./setup.py test

# includes every python file so we can ensure nothing remains untested / unused
coverage_include='*.py'
coverage_omit='venv/*,.eggs/*'

# if we're running this from a tty (our laptop), make html (but don't fail)
if [ -t 1 ]; then
coverage html --include="$coverage_include" --omit="$coverage_omit" && \
  echo_bold "\nHtml test report generated at:\n\t$script_dir/htmlcov/index.html\n" || \
  echo 'Could not make html coverage report.' >&2
fi

# always run the usual report function and fail on on low coverage
# TODO increase coverage to 100
coverage report --include="$coverage_include" --omit="$coverage_omit" --fail-under=90

exit 0
