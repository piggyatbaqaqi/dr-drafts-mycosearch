#!/bin/bash
# Pass all arguments to build_index.sh to support optional Redis parameters
./build_index.sh "$@"
./prompts/sample_prompt2cli.sh
