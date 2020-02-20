# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import re
from sys import stderr, exit
from math import floor
import zipfile
import xml.etree.ElementTree as eTree
from signal import signal, SIGPIPE, SIG_DFL
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.py')) as f: exec(f.read(), version)

# A function to quit with an error:
def error(msg, exit_code=1):
    print('ERROR: {}'.format(msg), file=stderr)
    exit(exit_code)

def process_eds(input_file):
    # Open the EDF zip file:
    try: zip_file = zipfile.ZipFile(input_file, mode='r')
    except: error('failed to open EDS file "{}"'.format(input_file))
    
    # Get the multicomponent file by its name:
    filename_re = re.compile('.*multicomponentdata\\.xml$')
    filename = None
    for f in zip_file.infolist():
        if filename_re.match(f.filename) != None:
            filename = f.filename
            break
    if filename is None: error('multicimponent XML data not present')
    mc_file = zip_file.open(filename, 'r')

    # Parse the XML file:
    tree = eTree.parse(mc_file)
    root = tree.getroot()

    # Extract the well number:
    well_n = int(root.find('WellCount').text)
    cycle_n = int(root.find('CycleCount').text)

    # Extract the dye lists:
    dye_list = {}
    for dyelist in root.findall('DyeData'):
        well_index = int(dyelist.attrib['WellIndex'])
        dye_data = dyelist.find('DyeList').text.strip('[]').split(', ')
        dye_list[well_index] = dye_data

    # Extract the signal data:
    signal_data = {}
    for well_signalset in root.findall('SignalData'):
        well_index = int(well_signalset.attrib['WellIndex'])
        signal_data[well_index] = {}
        cycle_datasets = well_signalset.findall('CycleData')
        for i in range(len(cycle_datasets)):
            signal_data[well_index][dye_list[well_index][i]] = [float(x) for x in cycle_datasets[i].text.strip('[]').split(', ')]

    # Close the ZIP file:
    zip_file.close()

    # Print out the data:
    print('well\tcycle\tROX\tFAM')
    for well in range(well_n):
        for cycle in range(cycle_n):
            print('{}\t{}\t{:.2f}\t{:.2f}'.format(well + 1, cycle + 1, signal_data[well]['ROX'][cycle], signal_data[well]['FAM'][cycle]))

def process_amp(input_file):
    signal_data = {}
    try:
        with open(input_file, 'rt') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('#') or (len(line) == 0) or (line.startswith('Experiment Name')): continue
                line_data = line.split('\t')
                well = line_data[2]
                if well not in signal_data.keys():
                    signal_data[well] = {}
                    signal_data[well]['data'] = {}
                    signal_data[well]['row'] = well[0]
                    signal_data[well]['col'] = int(well[1:])
                cycle = floor(float(line_data[8]))
                rox = float(line_data[9])
                fam = float(line_data[5]) * rox
                signal_data[well]['data'][cycle] = {'ROX':rox, 'FAM':fam}
    except: error('failed to open amplification text file "{}"'.format(input_file))

    # Convert the well IDs to an index:
    rows = sorted(list(set([signal_data[well]['row'] for well in signal_data.keys()])))
    cols = sorted(list(set([signal_data[well]['col'] for well in signal_data.keys()])))
    ncol = len(cols)
    row_offset = dict(zip(rows, [rows.index(i) * ncol for i in rows]))
    well_map = {}
    for row in rows:
        for col in cols:
            well_map[row_offset[row] + col] = '{}{}'.format(row, col)

    # Print out the data:
    print('well\tcycle\tROX\tFAM')
    for well in sorted(list(well_map.keys())):
        try: well_data = signal_data[well_map[well]]
        except: error('missing data for well {}'.format(well))
        for cycle in sorted(well_data['data'].keys()):
            print('{}\t{}\t{:.2f}\t{:.2f}'.format(well, cycle, well_data['data'][cycle]['ROX'], well_data['data'][cycle]['FAM']))

def process_multicomponent():
    # Set up the command line arguments & parse them:
    parser = argparse.ArgumentParser(description = 'Parse out intensity data from a ThermoFisher data files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument(dest='format', choices=['eds', 'amp'], help='input file format')
    parser.add_argument(dest='input_file', help='the input amplification file')
    args = parser.parse_args()

    # Play nicely with head:
    signal(SIGPIPE, SIG_DFL)
    
    #Fire off the subcommands:
    if args.format == 'eds': process_eds(args.input_file)
    if args.format == 'amp': process_amp(args.input_file)

def process_targets():
    # Set up the command line arguments & parse them:
    parser = argparse.ArgumentParser(description = 'Extract well data from an EDS file')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument(dest='input_file', help='the input EDS file')
    args = parser.parse_args()

    # Open the EDF zip file:
    try: zip_file = zipfile.ZipFile(args.input_file, mode='r')
    except: error('failed to open EDS file "{}"'.format(input_file))

    # Get the plate_setup file by its name:
    filename_re = re.compile('.*plate_setup\\.xml$')
    filename = None
    for f in zip_file.infolist():
        if filename_re.match(f.filename) != None:
            filename = f.filename
            break
    if filename is None: error('plate_setup XML data not present')
    ps_file = zip_file.open(filename, 'r')

    # Parse the XML file:
    tree = eTree.parse(ps_file)
    root = tree.getroot()

    # Extract the well dimensions:
    row_n = int(root.find('Rows').text)
    col_n = int(root.find('Columns').text)
    well_n = row_n * col_n

    # Object to hold the well data:
    well_data = {}

    # Iterate through the FeatureMaps:
    for featureMap in root.findall('FeatureMap'):
        feature_id = featureMap.find('Feature').find('Id').text
        if feature_id != 'detector-task': continue
        for wellFeature in featureMap.findall('FeatureValue'):
            well_index = int(wellFeature.find('Index').text)
            well_data[well_index] = wellFeature.find('FeatureItem').find('DetectorTaskList').find('DetectorTask').find('Detector').find('Name').text

    # Close the ZIP file:
    zip_file.close()

    # Print out the data:
    print('well\ttarget')
    for well in range(well_n):
        print('{}\t{}'.format(well + 1, well_data[well]))
