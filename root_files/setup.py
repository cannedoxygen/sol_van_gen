#!/usr/bin/env python
"""
Setup script for the CMYK Retro Lo-Fi Solana Vanity Generator
"""

from setuptools import setup, find_packages
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Get version
__version__ = '1.0.0'

setup(
    name="cmyk-solana-vanity",
    version=__version__,
    description="CMYK Retro Lo-Fi Solana Vanity Address Generator",
    author="Canned Oxygen",
    author_email="cannedoxygen.com",
    url="https://github.com/cannedoxygen/sol_van_gen",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        'console_scripts': [
            'cmyk-vanity=main:main',
        ],
    },
    python_requires='>=3.7',
    keywords="solana, vanity, address, cryptocurrency, blockchain, cmyk, retro",
    package_data={
        '': ['assets/*', 'assets/**/*'],
    },
)