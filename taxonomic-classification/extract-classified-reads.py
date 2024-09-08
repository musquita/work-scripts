#!/usr/bin/env python3
# ============================================================================
# Extract specific classified reads from (combined) Kraken2 reports
# ============================================================================
#
# Written to facilitate extraction of reads from (combined) Kraken2 reports
# Interactively: designed to be user-friendly for teammates with limited Linux experience
# Script able to process reports in multiple directories, or a single one
# classification bash script must be previously run, or folder structure maintained.
#
# Author: Cristina S. Mesquita
# Date: September 2024
# Version: 1.1
#
# ============================================================================

import os
import glob
import subprocess
import argparse
import tempfile
from typing import List, Optional
# versatility: use of argparse allows interactive script usage or with cl arguments

# Function to define default values for optional user prompts. Deals with cases when user does not provide input
def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    user_input = input(f"{prompt} [{default}]: ").strip() if default else input(f"{prompt}: ").strip()
    return user_input if user_input else default

# Function to execute commands - handles errors and outputs~
def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error: {e.stderr}")
        exit(1)

def find_db_dir(kraken2_dir: str, db_specific: str) -> Optional[str]:
    for root, dirs, _ in os.walk(kraken2_dir):
        if db_specific in dirs:
            return os.path.join(root, db_specific)
    return None

# glob.glob() finds all .k2report files at dir - takes first file found and extracts sample name
def find_k2report_files(directory: str) -> List[str]:
    return glob.glob(os.path.join(directory, "**/*.k2report"), recursive=True)

# adjusted main function for code reusability - now process_sample  encapsulates the logic for processing a single sample
def process_sample(sample: str, experiment_dir: str, kraken2_dir: str, db_specific: str, seq_file_type: str, fastq_output: bool, args: argparse.Namespace) -> None:
    # Extract information based on presence/absence of db argument
    # With os.walk() you recursively look for corresponding folder in kraken2_dir
    if db_specific:
        db_dir = find_db_dir(kraken2_dir, db_specific)
        if db_dir is None:
            print(f"Folder named {db_specific} not found within {kraken2_dir}")
            exit(1)
        kreport = os.path.join(db_dir, f"{sample}.k2report")
        class_file = os.path.join(db_dir, f"{sample}.k2")
    else:
        kreport = os.path.join(kraken2_dir, f"{sample}_combined.k2report")
        class_files = glob.glob(os.path.join(kraken2_dir, f"**/{sample}.k2"), recursive=True)
        combined_class_file = os.path.join(kraken2_dir, f"{sample}_combined.k2")
        with open(combined_class_file, 'w') as outfile:
            for class_file in class_files:
                with open(class_file, 'r') as infile:
                    outfile.write(infile.read())
        class_file = combined_class_file

    # Define path to potential fastq input files
    raw_seq_file = os.path.join(experiment_dir, "basecall", f"{sample}.fastq")
    masked_seq_file = os.path.join(kraken2_dir, f"{sample}_masked.fastq")
    # Determine the file type based on user input passed from main
    if seq_file_type.lower() == 'raw':
        seq_file = raw_seq_file
    elif seq_file_type.lower() == 'masked':
        seq_file = masked_seq_file
    else:
        print("Invalid option. Extracting from raw file as default.")
        seq_file = raw_seq_file

    # Edit k2report to remove comment lines
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_kreport:
        run_command(f"sed '/^#/d' {kreport} > {temp_kreport.name}")
        kreport = temp_kreport.name

    # Get taxonomic IDs
    taxids = args.taxids or get_user_input("Input taxonomy ID[s] to extract or exclude (space-delimited)").split()
    # Check for including children first
    include_children = args.include_children or get_user_input("Include classified reads in levels below specified taxid(s)? (yes/no)").lower() == 'yes'
    # Only ask about parents if children are not included
    include_parents = args.include_parents or (not include_children and get_user_input("Include classified reads in levels above specified taxid(s)? (yes/no)").lower() == 'yes')

    # Execute extract_kraken_reads.py from KrakenTools
    taxid_str = '-'.join(taxids)
    if fastq_output :
        output_file = f"{sample}-{taxid_str}-extract.fastq"
    else:
        output_file = f"{sample}-{taxid_str}-extract.fasta"

    command = f"extract_kraken_reads.py -k {class_file} -s {seq_file} -t {' '.join(taxids)} -o {output_file} -r {kreport}"
    # Add extra parameters if required
    if include_children:
        command += " --include-children"
    if include_parents:
        command += " --include-parents"
    if args.exclude:
        command += " --exclude"
    if args.fastq_output:
        command += " --fastq-output"

    run_command(command)
    print(f"Extracted reads were saved at: {os.path.abspath(output_file)}")

    # Cleanup
    os.unlink(kreport)
    if not db_specific:
        os.unlink(combined_class_file)

def main():
    parser = argparse.ArgumentParser(description="Extract Kraken2-classified reads.")
    parser.add_argument("--experiment_dir", help="Directory of corresponding Experiment/Sample folder")
    parser.add_argument("--db", help="Single database classification to process")
    parser.add_argument("--taxids", nargs='+', help="Taxonomy ID[s] of reads to extract (space-delimited)")
    parser.add_argument("--include-children", action="store_true", help="Include reads classified more specifically than the specified taxids")
    parser.add_argument("--include-parents", action="store_true", help="Include reads classified at parent levels of the specified taxids")
    parser.add_argument("--exclude", action="store_true", help="Instead of finding matching reads, finds all reads NOT matching specified taxids")
    parser.add_argument("--fastq-output", action="store_true", help="Print output FASTQ reads [requires input FASTQ, default: output is FASTA]")

    args = parser.parse_args()

    print("This script assumes classification has been run, or folder structure is kept.")
    # Prompting user for undefined arguments (global inputs)
    experiment_dir = args.experiment_dir or get_user_input("Input the Experiment/Sample directory you wish to process")
    seq_file_type = get_user_input("Do you wish to extract raw or masked reads for all samples? (raw/masked)")
    fastq_output = args.fastq_output or get_user_input("Do you want FASTQ output for all samples? (yes/no)").lower() == 'yes'
    
    # cd to kraken2 folder
    kraken2_dir = os.path.join(experiment_dir, "analysis", "kraken2")
    if not os.path.exists(kraken2_dir):
        print(f"The directory {kraken2_dir} does not exist.")
        exit(1)
    os.chdir(kraken2_dir)

    # Check if aim is to extract from all classifeid databases or a specific one
    db_specific = args.db or get_user_input("To only extract reads based on classifications from a single-database, please input folder name (leave blank if not)")
    # Find all sample names
    if db_specific:
        db_dir = find_db_dir(kraken2_dir, db_specific)
        if db_dir is None:
            print(f"Folder named {db_specific} not found within {kraken2_dir}")
            exit(1)
        k2report_files = find_k2report_files(db_dir)
    else:
        k2report_files = find_k2report_files(kraken2_dir)
    if not k2report_files:
        print(f"No .k2report files found in the specified directory.")
        exit(1)

    samples = list(set(os.path.splitext(os.path.basename(file))[0] for file in k2report_files))

    if len(samples) > 1:
        print(f"Found multiple samples: {', '.join(samples)}")
        process_all = get_user_input("Do you want to process all samples? (yes/no)").lower() == 'yes'
        if not process_all:
            sample = get_user_input("Which sample do you want to process?", samples[0])
            samples = [sample]
    for sample in samples:
        print(f"Processing sample: {sample}")
        process_sample(sample, experiment_dir, kraken2_dir, db_specific, seq_file_type, fastq_output, args)

if __name__ == "__main__":
    main()
