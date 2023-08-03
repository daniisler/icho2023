#!/bin/bash

PROJECT=$( pwd )

export PYTHONPATH="${PROJECT}:${PYTHONPATH}"
export PATH="${PROJECT}/bin:${PATH}"

unset PROJECT
