#!/bin/bash
# Pass all arguments to build_index.py to support optional Redis parameters
python src/build_index.py "$@"
./prompts/sample_prompt2cli.sh
