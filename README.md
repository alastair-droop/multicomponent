# Extract multicomponent (FAM & ROX) data from Thermo Fisher EDS and amplification files

This script allows extraction of multicomponent data from Thermofisher `EDS` or amplification files.

## Installation

Installation should be as simple as:

~~~bash
git clone https://github.com/alastair-droop/multicomponent.git
cd multicomponent
python setup.py install
~~~

## Usage

### Multicomponent Processing

EDS files can be directly converted to multicomponent format:

~~~bash
multicomponent eds <file.eds>
~~~

Similarly, amplification files (from the ThermoFisher online tools) can be converted:

~~~bash
multicomponent amp <file.txt>
~~~

### Well Targets from EDS Files

Well target labels can be extracted from EDS files:

~~~bash
eds-targets <file.eds>
~~~

## Licence

These tools are released under the [GNU General Public License version 3](http://www.gnu.org/licenses/gpl.html).
