#!/usr/bin/env sh

python -m pytest -v

echo ""
echo "========================MYPY======================"
mypy river --warn-return-any --warn-unreachable

echo ""
echo "========================TODO======================="
grep --color=auto -r "FIXME" river
grep --color=auto -r "TODO" river
grep --color=auto -r "TODO" tests
