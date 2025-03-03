#!/bin/bash

# Check if the argument (file name) is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 input.csv"
    exit 1
fi

input_file="$1"
output_file="${input_file%.csv}_out.csv"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

# Process the file using awk
awk '
BEGIN { FS=","; OFS="," }
NR == 1 { print; next }  # Keep the header unchanged
{
    n = NF  # Get the total number of fields
    last2 = $(n-1) "," $n  # Extract the last two fields (date and group_name)
    sub("," last2 "$", "", $0)  # Remove them from the original string
    print "\"" $0 "\"", last2  # Quote the tokens field and reconstruct the line
}
' "$input_file" > "$output_file"

echo "File processed: $output_file"
