#!/bin/bash
set -e  # Exit on any error

############################################################
# (Optional) Activate the Conda environment if not auto-activated
############################################################
# If your Dockerfile does not already set SHELL ["conda", "run", ...], 
# uncomment the line below. This ensures we run inside 'bamboozler_env'.
# source activate bamboozler_env || conda activate bamboozler_env
# Note: The exact command depends on your conda setup in the container.

echo "🔹 Checking Core System & Python Environment"
which python3
python3 --version
python3 -c "import sys; print('Python sys.version:', sys.version)"
which pip
pip list  # Ensure required Python packages are installed

echo "🔹 Checking Python Package Imports"
python3 -c "import Bio.SeqIO; print('Biopython (SeqIO) is installed')"
python3 -c "from pyfaidx import Fasta, FetchError; print('pyfaidx is installed')"
python3 -c "import argparse; print('argparse is installed')"
python3 -c "import logging; print('logging is installed')"
python3 -c "import os; print('os is available')"
python3 -c "import random; print('random is available')"
python3 -c "import requests; print('requests is installed')"
python3 -c "import shutil; print('shutil is available')"
python3 -c "import subprocess; print('subprocess is available')"
python3 -c "import sys; print('sys is available')"
python3 -c "import yaml; print('yaml is installed')"

echo "🔹 Checking Reference Genome Downloading Tools"
which wget       || echo "wget not found (optional)"
which curl       || echo "curl not found!"
which rsync      || echo "rsync not found (optional)"
which samtools   || echo "samtools not found!"
which bgzip      || echo "bgzip not found (optional if htslib is installed in a different path)"
which tabix      || echo "tabix not found (optional if htslib is installed in a different path)"

echo "🔹 Checking Python Packages for Reference Data"
python3 -c "import pyfaidx; print('pyfaidx is installed')"
python3 -c "import Bio; print('Biopython is installed')"
python3 -c "import refgenconf; print('refgenconf is installed')"

echo "🔹 Checking Gene Annotation Retrieval Tools"
which bedtools   || echo "bedtools not found!"
which awk        || echo "awk not found!"
which grep       || echo "grep not found!"

echo "🔹 Checking Python Packages for Gene Annotation Handling"
python3 -c "import gffutils; print('gffutils is installed')"
python3 -c "import pybedtools; print('pybedtools is installed')"

echo "🔹 Checking BAM File Generation & Handling Tools"
which samtools   || echo "samtools not found!"
which bcftools   || echo "bcftools not found!"
which bedtools   || echo "bedtools not found!"

echo "🔹 Checking Python Packages for BAM Processing"
python3 -c "import pysam; print('pysam is installed')"

echo "🔹 Checking Variant Addition/Editing Tools"
which neat       && neat --help  || echo "NEAT not found or not on PATH"
# VarSim does not always install a 'varsim' or 'varsim.py' in PATH; 
# you might need to check /opt/varsim or a script location. Example:
[ -f /opt/varsim/varsim.py ] && echo "VarSim is present in /opt/varsim" || echo "VarSim not found at /opt/varsim"

echo "🔹 Checking Python Packages for Variant Handling"
python3 -c "import vcfpy; print('vcfpy is installed')"
python3 -c "import pysam; print('pysam is installed again for variant-handling check')"

echo "🔹 Checking BamSurgeon Scripts"
# BamSurgeon’s main scripts are typically addsv.py, addsnv.py, addindel.py in /opt/bamsurgeon/bin
[ -f /opt/bamsurgeon/bin/addsv.py ] && echo "BamSurgeon addsv.py is present" || echo "BamSurgeon addsv.py not found"
python3 -c "import bamsurgeon; print('BamSurgeon Python module is importable')" || echo "BamSurgeon Python module not found"

echo "🔹 Checking User-Supplied BAM Directory"
ls -lh /data/ || echo "/data/ not found (optional)"

echo "🔹 Checking Input Handling & CLI Processing"
which argparse  || echo "argparse is built-in, 'which' might not show it"

echo "🔹 Checking Additional Bioinformatics Tools (from Dockerfile)"
which bwa        || echo "bwa not found!"
which picard     || echo "picard not found (con might be installed as a jar only)!"
which exonerate  || echo "exonerate not found!"
which velvet     || echo "velvet not found!"
which htslib     || echo "htslib not found!"

echo "🔹 Checking Required System Dependencies"
which curl
which git
which gcc
which make
which autoconf
# Developer headers (zlib1g-dev, libglib2.0-dev etc.) may not appear as "which zlib1g-dev"
# because they're not executables. We'll just trust that apt-get installed them.
# Or we can do dpkg -s <package> if needed.

which java       || echo "Java not found!"
which mvn        || echo "Maven not found!"

echo "🔹 Verifying Cleanup of Unused Packages"
ls -lh /var/lib/apt/lists/ || echo "No apt lists directory found"

echo "✅ Environment check complete!"

