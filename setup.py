from setuptools import setup, find_packages
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'multicomponent', 'version.py')) as f: exec(f.read(), version)

setup(
    name = 'multicomponent',
    version = version['__version__'],
    description = 'Simple tools to extract multicomponent (FAM & ROX) data from Thermo Fisher EDS and amplification files',
    author = 'Alastair Droop',
    author_email = 'alastair.droop@gmail.com',
    url = 'https://github.com/alastair.droop/multicomponent',
    classifiers = [
    ],
    packages = find_packages(),
    install_requires = [
    ],
    python_requires = '>=3',
    entry_points = {
        'console_scripts': [
            'multicomponent=multicomponent.scripts:process_multicomponent',
            'eds-targets=multicomponent.scripts:process_targets'
        ]
    }
)
