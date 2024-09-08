#!/usr/bin/env python
# ============================================================================
# POD5 processing python script to extract read_ids
# ============================================================================
#
# Author: Cristina S. Mesquita
# Date: July 2024
# Version: 1.0
#
# ============================================================================

import pandas as pd
import argparse

def filter_read_ids(input_file, output_file, adaptive_file):
    # Load the CSV file
    df = pd.read_csv(input_file, delimiter='\t')  # Change delimiter if necessary

    # Strip any leading/trailing whitespace from the column names
    df.columns = df.columns.str.strip()

    # Check if the 'end_reason' column exists
    if 'end_reason' not in df.columns:
        print("Error: 'end_reason' column not found in the CSV file.")
        print("Available columns:", df.columns)
        return

    # Filter the DataFrame
    filtered_df = df[df['end_reason'] != 'data_service_unblock_mux_change']
    # Extract the read_ids
    read_ids = filtered_df['read_id']
    # Check if DataFrames has more than 0 rows before saving to text files
    if not read_ids.empty:
        read_ids.to_csv(output_file, index=False, header=False)
        print(f"Read_ids to be basecalled saved to {output_file}")
    else:
        print("No read_ids to be basecalled found.")

    # Check if there are any adaptive sampling entries before creating the DataFrame
    adaptive_entries = df['end_reason'] == 'data_service_unblock_mux_change'
    if adaptive_entries.any():
        adaptive_df = df[adaptive_entries]
        adaptive_read_ids = adaptive_df['read_id']
        adaptive_read_ids.to_csv(adaptive_file, index=False, header=False)
        print(f"Adaptive sampling read_ids saved to {adaptive_file}")
    else:
        print("No adaptive sampling read_ids found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter read_ids based on end_reason.')
    parser.add_argument('input_file', type=str, help='Path to the CSV file from pod5 view.')
    parser.add_argument('output_file', type=str, help='Path to the text file for read_ids to basecall.')
    parser.add_argument('adaptive_file', type=str, help='Path to the text file for adaptive sampling read_ids.')

    args = parser.parse_args()

    filter_read_ids(args.input_file, args.output_file, args.adaptive_file)
