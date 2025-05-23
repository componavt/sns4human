#!/bin/bash
# Count total number of lines in all CSV files in current directory (excluding headers)
find . -name "*.csv" -exec tail -n +2 {} \; | wc -l
