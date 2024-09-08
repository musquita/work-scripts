#!/usr/bin/env python
# ============================================================================
# Combination of multiple Bracken output files
# ============================================================================
# Based on the script in Bracken by Jennifer Lu
#
# Edited to create a tot_num and tot_frac columns when combining files
#
# Author: Cristina S. Mesquita
# Date: June 2024
# Version: 1.0
#
# ============================================================================

import os, sys, argparse
from time import gmtime
from time import strftime 

#Main method
def main():
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', dest='files', 
        nargs='+', type=str, required=True,
        help='Bracken output files to combine.')
    parser.add_argument('--names', dest='names', 
        default='',required=False,
        help='Names for each input file - to be used in column headers of output [separate names with commas]')
    parser.add_argument('-o', '--output', dest='output', required=True,
        help='Name of output file with combined Bracken results.')
    args = parser.parse_args()

    #Start program
    time = strftime("%m-%d-%Y %H:%M:%S", gmtime())
    sys.stdout.write("PROGRAM START TIME: " + time + '\n')

    #Initialize variables 
    sample_counts = {}  #species :: sample1: counts, samples2: counts 
    total_reads = {}    #sample1: totalcounts, sample2: totalcounts 
    all_samples = []
    #Get sample names
    if len(args.names) == 0:
        for f in args.files:
            curr_sample = os.path.basename(f)
            total_reads[curr_sample] = 0
            all_samples.append(curr_sample)
    else:
        for curr_sample in args.names.split(","):
            total_reads[curr_sample] = 0
            all_samples.append(curr_sample) 
    #Read each file information in 
    level = ''
    i = 0
    for f in args.files:
        #Print update
        curr_name = all_samples[i]
        i += 1
        sys.stdout.write("Processing Output File %s:: Sample %s\n" % (f, curr_name))
        #Iterate through file
        header = True
        i_file = open(f,'r')
        for line in i_file:
            #Header line
            if header:
                header=False
                continue
            #Process line 
            [name, taxid, taxlvl, kreads, areads, estreads, frac] = line.strip().split("\t")
            estreads = int(estreads) 
            #Error Checks
            if name not in sample_counts:
                sample_counts[name] = {}
                sample_counts[name][taxid] = {}
            elif taxid != list(sample_counts[name].keys())[0]:
                sys.exit("Taxonomy IDs not matching for species %s: (%s\t%s)" % (name, taxid, sample_counts[name].keys()[0]))
            if len(level) == 0:
                level = taxlvl 
            elif level != taxlvl:
                sys.exit("Taxonomy level not matching between samples")
            #Save counts
            total_reads[curr_name] += estreads
            sample_counts[name][taxid][curr_name] = estreads 
        #Close file 
        i_file.close()

    #Print output file header
    o_file = open(args.output, 'w')
    o_file.write("name\ttaxonomy_id\ttaxonomy_lvl")
    for name in all_samples:
        o_file.write("\t%s_num\t%s_frac" % (name,name))
    o_file.write("\ttotal_num\ttotal_frac\n")
    
    # Calculate total number of reads across all samples
    total_num_all_samples = sum(total_reads.values())
    # Initialize dictionary to store total counts
    total_counts = {}
    # Iterate over the sample counts dictionary to calculate total counts
    for name, taxon_counts in sample_counts.items():
        total_counts[name] = sum(sum(sample.values()) for sample in taxon_counts.values())

    #Print each sample 
    for name in sample_counts:
        #Print information for classification
        taxid = list(sample_counts[name].keys())[0]
        o_file.write("%s\t%s\t%s" % (name, taxid, level)) 
        total_num = 0

        #Calculate and print information per sample 
        for sample in all_samples:
            if sample in sample_counts[name][taxid]:
                num = sample_counts[name][taxid][sample]
                perc = float(num)/float(total_reads[sample])
                o_file.write("\t%i\t%0.5f" % (num,perc))
                total_num += num
            else:
                o_file.write("\t0\t0.00000")
        
        # Calculate total fraction for this species
        total_frac = total_num / total_num_all_samples if total_num_all_samples != 0 else 0
        
        o_file.write("\t%i\t%0.5f\n" % (total_num, total_frac))
    
    o_file.close()

    #End program
    time = strftime("%m-%d-%Y %H:%M:%S", gmtime())
    sys.stdout.write("PROGRAM END TIME: " + time + '\n')

if __name__ == "__main__":
    main()
