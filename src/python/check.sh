#!/usr/bin/env sh

pytest -v

echo ""
echo "========================MYPY======================"
mypy river
