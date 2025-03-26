#!/bin/bash
cd src/spyllm/visualization/frontend 
echo "Installing npm dependencies..."
npm i --silent &> /dev/null
echo "Building frontend..."
npm run -s build &> /dev/null
echo "Launching SpyLLM UI"
cd -
PYTHONPATH=$PYTHONPATH:$(pwd)/src SPYLLM_INTERNAL=ui python src/spyllm/visualization/app.py