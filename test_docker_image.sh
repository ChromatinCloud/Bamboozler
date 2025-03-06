#!/bin/bash

echo "🚀 Running BamBoozler Post-Install Tests 🚀"

# 1️⃣ Check Python, Conda, and Mamba installation
echo "🔍 Checking Python and Conda/Mamba installation..."
python --version || echo "❌ Python not found!"
conda --version || echo "❌ Conda not found!"
mamba --version || echo "❌ Mamba not found!"

# 2️⃣ Check if BamSurgeon dependencies are installed
echo "🔍 Verifying BamSurgeon dependencies..."
python3 -O /opt/bamsurgeon/scripts/check_dependencies.py || echo "❌ BamSurgeon dependencies check failed!"

# 3️⃣ Verify installed bioinformatics tools
echo "🔍 Checking installed bioinformatics tools..."
samtools --version || echo "❌ Samtools not found!"
bwa || echo "❌ BWA not found!"
picard -h || echo "❌ Picard not found!"
exonerate -h || echo "❌ Exonerate not found!"
velvetg --help || echo "❌ Velvet not found!"

# 4️⃣ Check NEAT and VarSim availability
echo "🔍 Checking NEAT and VarSim..."
neat-genreads.py --help || echo "❌ NEAT not found!"
varsim --help || echo "❌ VarSim not found!"

# 5️⃣ Verify BamBoozler CLI is working
echo "🔍 Checking BamBoozler CLI..."
bamboozler --help || echo "❌ BamBoozler CLI not found!"

# 6️⃣ Run a BamSurgeon variant editing test
echo "🔍 Running BamSurgeon variant editing test..."
python3 -O /opt/bamsurgeon/bin/addsnv.py \
    -v test_data/test_snv.txt \
    -f test_data/testregion_realign.bam \
    -r test_data/Homo_sapiens_chr22_assembly19.fasta \
    -o test_data/testregion_snv_mut.bam \
    --aligner bwa || echo "❌ BamSurgeon test failed!"

# 7️⃣ Run a full BamBoozler variant edit test
echo "🔍 Running BamBoozler variant edit test..."
bamboozler variant \
    --bam test.bam \
    --bai test.bai \
    --reference ref.fasta \
    --vcf test.vcf \
    --output-dir variant_output \
    --output-name modified_sample \
    --variant-tool bamsurgeon || echo "❌ BamBoozler variant test failed!"

echo "✅ All tests complete! Check errors above if any test failed."

