from setuptools import setup, find_packages
import os, subprocess, glob

package_version = os.environ.get('GITHUB_REF_NAME', None)
if package_version is None:
    package_version = subprocess.check_output('git describe --tags'.split())
    package_version = package_version.strip().decode("utf-8")

with open('thumb2ISS/version.py', 'w') as f:
    f.write(f'__version__ = {package_version}\n')

# remove duplicate instructions from public package
for ins in glob.glob('thumb2ISS/instructions/[a-z]*.py'):
    os.remove(ins)

setup(
    name='thumb2ISS',
    version=package_version,
    packages=find_packages('.', exclude=["test"]),
    license='BSD-3-Clause',
    include_package_data=True,
    install_requires=[
        'Click>=8.0.0', 'intelhex>=2.3.0'
    ],
    description='Thumb2 Instruction Set Simulator, allowing to run and debug code compiled for ARM Cortex-M on PC.',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish
        "License :: OSI Approved :: BSD License",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'thumb2ISS = thumb2ISS.thumb2ISS:run',
        ],
    },
)
