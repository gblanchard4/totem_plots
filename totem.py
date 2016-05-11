#!/usr/bin/env python
import argparse
import matplotlib.pyplot as plt
import sys

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''
Create a totem plot!
'''


def clean_taxa_string(taxa):
    # Replace brackets
    chars = ['[', ']']
    for char in chars:
        taxa = taxa.replace(char, '')
    # Remove 'u' formatting strings
    taxa = taxa.replace("u'k__", "k__")
    taxa = taxa.replace("u'p__", "p__")
    taxa = taxa.replace("u'c__", "c__")
    taxa = taxa.replace("u'o__", "o__")
    taxa = taxa.replace("u'f__", "f__")
    taxa = taxa.replace("u'g__", "g__")
    taxa = taxa.replace("u's__", "s__")
    # Remove remaining '
    taxa = taxa.replace("'", '')
    # Remove extra whitespace between levels
    taxa = taxa.replace(", ", ",")
    return taxa


def get_core(files, level):
    cores = []
    for filename in files:
        with open(filename, 'r') as handle:
            for line in handle:
                if not line.startswith('#'):
                    taxa = line.rstrip().split('\t')[1]
                    # Strip extra characters
                    taxa = clean_taxa_string(taxa)
                    # Cut taxa to desired taxa level
                    # and return a proper formated string
                    taxa = ';'.join(taxa.split(',')[0:4])
                    cores.append(taxa)
    return list(set(cores))


def get_headers_from_table(table):
    with open(table, 'r') as handle:
        for line in handle:
            # Grab the column names
            if line.startswith("#OTU ID"):
                otuid, name1, name2 = line.lstrip('#').rstrip().split('\t')
    return otuid, name1, name2


def get_values_from_table(table):
    otus = []
    col1s = []
    col2s = []
    with open(table, 'r') as handle:
        for line in handle:
            # Get the values for each OTU
            if not line.startswith('#'):
                otu, col1, col2 = line.rstrip().split('\t')
                otus.append(otu)
                col1s.append(col1)
                col2s.append(col2)
    return otus, col1s, col2s


def main():
    # Argument Parser
    parser = argparse.ArgumentParser(description='<This is what the script does>')

    # Input file
    parser.add_argument('-i', '--input', dest='input', required=True, help='The input biom to totemize. MUST BE A TXT')
    # Output file
    parser.add_argument('-o', '--output', dest='output', required=True, help='The output file')
    # Core files
    parser.add_argument('-c', '--core', dest='core', nargs=2, help='The core OTUs to subset to. i.e. core_otus_100.txt')
    # Taxa Level
    parser.add_argument('-l', '--level', dest='level', type=int, help='The taxa level to plot. Required if core is supplied.')
    # Percent
    parser.add_argument('-p', '--percent', dest='percent', type=int, help='The minimum percent present to make it to the plot')
    # Sorted
    parser.add_argument('-s', '--sort', dest='sort', action='store_true', help='Sort the plot')

    # Parse arguments
    args = parser.parse_args()
    infile = args.input
    outfile = args.output
    core_files = args.core
    level = args.level
    percent = args.percent
    sort = args.sort

    if core_files:
        if not level:
            sys.exit("You must supple a taxa level if core is included")
        else:
            core_otus = get_core(core_files, level)

    # Get the column headers
    otu, col1_name, col2_name = get_headers_from_table(infile)

    # Get the data values
    otu_names, col1_data, col2_data = get_values_from_table(infile)

    # Cast values to floats
    col1_data = [float(i) * 100 for i in col1_data]
    col2_data = [-(float(i) * 100) for i in col2_data]

    # Remove empty otus
    nonempty_otu_names = []
    nonempty_col1_data = []
    nonempty_col2_data = []
    for index, otu in enumerate(otu_names):
        if not col1_data[index] == 0 and not col2_data[index] == 0:
            nonempty_otu_names.append(otu_names[index])
            nonempty_col1_data.append(col1_data[index])
            nonempty_col2_data.append(col2_data[index])
    otu_names = nonempty_otu_names
    col1_data = nonempty_col1_data
    col2_data = nonempty_col2_data

    # Plot based on arguments passed
    if core_files:
        core_otu_names = []
        core_col1_data = []
        core_col2_data = []
        for index, otu in enumerate(otu_names):
            if otu in core_otus:
                core_otu_names.append(otu_names[index])
                core_col1_data.append(col1_data[index])
                core_col2_data.append(col2_data[index])
        otu_names = core_otu_names
        col1_data = core_col1_data
        col2_data = core_col2_data
    if percent:
        percent_otu_names = []
        percent_col1_data = []
        percent_col2_data = []
        for index, otu in enumerate(otu_names):
            if col1_data[index] > percent or col2_data[index] > percent:
                percent_otu_names.append(otu_names[index])
                percent_col1_data.append(col1_data[index])
                percent_col2_data.append(col2_data[index])
        otu_names = percent_otu_names
        col1_data = percent_col1_data
        col2_data = percent_col2_data

    y_pos = range(len(otu_names))
    fig = plt.figure(figsize=(20, 15))
    # Create a horizontal bar in the position y_pos
    plt.barh(y_pos, col1_data, align='center', alpha=0.4, color='#263F13')
    plt.barh(y_pos, col2_data, align='center', alpha=0.4, color='#77A61D')

    # annotation and labels
    plt.xlabel('{}: Light Green. {}: Dark Green'.format(col2_name, col1_name))
    plt.title('Comparison of {} and {} Taxa'.format(col2_name, col1_name))
    plt.yticks(y_pos, otu_names)
    plt.ylim([-1, len(y_pos) + 0.1])
    plt.xlim([min(col2_data) - 5, max(col1_data) + 5])
    plt.grid()
    fig.tight_layout()
    plt.savefig('{}.png'.format(outfile))

if __name__ == '__main__':
    main()
