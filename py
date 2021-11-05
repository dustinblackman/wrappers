#!/usr/bin/env zsh

# Python executor that works with pyenv for version management.
# Uses poetry as a package manaeger, and handles installing it within a python versions scope for you.
# poetry-exec-plugin is installed along side poetry giving you the ability to save scripts in pyproject.toml
#
# Usage:
#   py install
#   py myfile.py
#   py my-script
#   py --help

set -e

function walkuptree() {
  local DIR=$(pwd)
  while [ ! -z "$DIR" ] && [ ! -f "$DIR/$1" ]; do
    DIR="${DIR%\/*}"
  done

  echo "$DIR/$1"
}

# Setup Python version
PYPROJECT_PATH=$(walkuptree pyproject.toml)
PYENV_VERSION=$((cat $PYPROJECT_PATH | grep 'python =' | awk -F '"' '{print $2}') 2> /dev/null || python3 -V | awk '{print $2}')

PYENV_VERSION_BIN="$PYENV_ROOT/versions/$PYENV_VERSION/bin"
[ ! -d "$PYENV_VERSION_BIN" ] && pyenv install "$PYENV_VERSION"
export PATH="$PYENV_VERSION_BIN:$PATH"

# Setup Poetry and poetry-exec-plugin
which poetry | grep -q '.pyenv' || (pip3 install poetry && pip3 install poetry-exec-plugin && poetry config virtualenvs.in-project true)

# Execute python script, exec script, poetry command, or any other binary.
pycmd=""
if [[ "$1" == *.py ]]; then
  pycmd="poetry run python $@"
elif (cat $PYPROJECT_PATH | sed -n '/poetry-exec-plugin/,/^\[/p' | grep '=' | awk '{print $1}' || echo '') | grep -q ^"$1"$; then
  [ ! -d "$(dirname $PYPROJECT_PATH)/.venv" ] && poetry install
  pycmd="poetry exec $@"
elif [[ "$1" =~ (--help|about|add|build|cache|check|config|debug|exec|env|export|help|init|install|lock|new|publish|remove|run|search|self|shell|show|update|version) ]]; then
  pycmd="poetry $@"
else
  pycmd="poetry run $@"
fi

# Support passing in stdin.
if [ ! -t 0 ]; then
  pycmd="cat - | $pycmd"
fi


eval "$pycmd"

# When running init, delete the virtualenv and recreate to make sure the correct python version has been installed.
if [[ "$1" == "init" ]]; then
  rm -rf .venv
  py echo "Done"
fi

