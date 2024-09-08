#!/bin/bash

# Fail on any error
set -e

GLOB_PATTERN=${1:-'**/*.md'}

markdownlint $GLOB_PATTERN
