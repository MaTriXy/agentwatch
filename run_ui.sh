#!/bin/bash
AGENTWATCH_INTERNAL=1 PYTHONPATH=$PYTHONPATH:$(pwd)/src poetry run python src/agentwatch/cli.py ui