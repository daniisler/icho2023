#!/bin/bash

PROJECT=$( pwd )

export PYTHONPATH="${PROJECT}/icho2023:${PYTHONPATH}"
export PATH="${PROJECT}/bin:${PATH}"

unset PROJECT
