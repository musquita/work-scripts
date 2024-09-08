# work-scripts

This repository contains various scripts designed to automate and simplify tasks related to infectious disease diagnostics based on long-read sequencing data.
These scripts rely on conda environments and are designed to be user-friendly, particularly for teammates with limited Linux experience. Parameters are prompted interactively to make the scripts easier to use. The conda environments are defined using a YAML file, listing the required software packages and their versions.

These scripts showcase my skills in data analysis, scripting, and problem-solving in bioinformatics workflows
I am currently reviewing a script that encompasses genome assembly, annotation, and antimicrobial resistance profiling in preparation for a future project. Phylogenetic analysis and potential transmission routes will also be studied *(still private)*.

## Bash Scripts Overview

- **mountU**: Mount an institute remote server with a prompt for user credentials.
- **POD5-export**: Export POD5 files to a remote server, considering the adaptive sampling flag and allowing multiple runs for the same experiment/sample.
- **basecall**: An automated workflow for basecalling long-read sequencing data with optional quality trimming.
- **classification**: An automated workflow for k-mer-based taxonomic classification.
- **local-blast**: A streamlined local BLAST analysis against the core-nt database, supporting various input formats and customizable parameters.

## Python Scripts Overview

- **extract-read-ids**: A script to extract read IDs from POD5 files based on the 'end_reason' flag.
- **combine-sequential-kreports**: Combines sequential Kraken2 reports, correcting the determination of unclassified reads.
- **combine-sequential-b-outputs**: Combines sequential Bracken outputs, creating columns to account for combined results.
- **extract-classified-reads**: Extracts specific classified reads from (combined) Kraken2 reports, from either single or multiple databases.

## Usage

Each script comes with its own set of instructions, outlining how to use it.
Please refer to the script headers or accompanying documentation for detailed information on parameters and dependencies.
To get started, ensure the specified conda environments are set up by using the provided YAML file.
