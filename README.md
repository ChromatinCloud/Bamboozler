# BamBoozler

### A Lightweight Bioinformatics Toolkit for:
1. **Reference Genome Download & Slicing**  
2. **Gene Annotation Retrieval**  
3. **BAM File Generation**  
4. **Variant Simulation & Editing**

With BamBoozler, you can quickly fetch reference FASTAs from Ensembl, slice specific loci, retrieve and filter annotations, generate synthetic BAM files, and add or edit variants with advanced control (e.g., 
allele frequency, read mix).

---

## Why BamBoozler?

- **Single Command** to slice out any region you care about—no more fighting with big `.fa.gz` references.  
- **Generate** brand new BAM files at any coverage depth, mutation rate, or apply real cancer-like signatures.  
- **Edit** an existing BAM’s variants with granular control or invoke external tools like NEAT, VarSim, or BAM surgeon.  
- **Simple CLI**: One tool, multiple subcommands.

---

## Installation Overview

> We offer **three** main ways to set up BamBoozler. Pick the one that best suits your environment:

1. **[Docker Setup](#docker-setup)**: The easiest for local desktops—no messing around with Python versions or tool dependencies.  
2. **[Conda Setup](#conda-setup)**: Common on HPC clusters and for users who already prefer conda or can’t run Docker.  
3. **[Pip Setup (Direct Python Installation)](#pip-setup-direct-installation)**: For the truly fearless who have Python 3.10+ installed locally.

---

## Docker Setup

If you **do** have Docker (or Docker Desktop) and want a quick “it just works” environment, do this:

1. **Install Docker**  
   - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)  
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)  
   - Linux: [Docker Engine on Linux](https://docs.docker.com/engine/install/) (often via apt, dnf, etc.)

2. **Build the Docker Image**  
   Open a terminal in BamBoozler’s root folder (where the `Dockerfile` is) and run:
```
   docker build -t bamboozler .
```

```markdown
This downloads a minimal Python image, installs BamBoozler and any external tools you’ve configured, and then saves it as an image named “bamboozler.”

### Run the Container
```bash
docker run -it bamboozler
```
You now have an **interactive shell** inside the container. Type:
```bash
bamboozler --help
```
or do something like:
```bash
bamboozler download --species human --build hg38 ...
```
All tools and dependencies are pre-installed. When you’re done, just type `exit` to leave.

**Pros**  
- Everything is self-contained.  
- No fiddling with Python on your system.

**Cons**  
- HPC clusters often don’t allow Docker.  
- Requires Docker to be installed (which can be a big download).

---

## Conda Setup

If you **cannot use Docker** (like on HPC) or already love conda, we provide a file `environment.yml` that includes both **Python** and **non-Python** dependencies (like samtools).

### Easy Way: `conda_setup.sh`

We include a script called `conda_setup.sh` that:

1. Checks if you have conda.  
2. If not found (on Linux x86_64), it downloads and installs Miniconda to `~/miniconda`.  
3. Creates or updates a conda environment called “bamboozler-env” from `environment.yml`.

**Steps**:

1. **Make script executable** (only once):
   ```
   chmod +x conda_setup.sh
   ```
2. **Run it**:
   ```
   ./conda_setup.sh
   ```
3. **Activate**:
   ```
   conda activate bamboozler-env
   ```
4. **Use BamBoozler**:
   ```
   bamboozler download --species human --build hg38 --chromosome 1 --start 1000000 --end 1001000 --output slice.fasta
   ```

That’s it! The script auto-installs Miniconda (if needed) and sets up your environment. HPC cluster usage may vary, especially if you can’t install to your home directory. In that case, ask your HPC admin or 
see if a conda module is already provided.

**Manual Conda** (if you prefer to do it yourself):
```
conda env create -f environment.yml
conda activate bamboozler-env
bamboozler --help
```

---

## Pip Setup (Direct Installation)

If you’re a dyed-in-the-wool Python user or you just want to do a quick local install:

1. **Check** your Python version:
   ```
   python --version
   ```
   Must be **Python 3.10+** (we recommend 3.10 to 3.13).

2. **Install** BamBoozler (and its Python dependencies):
   ```
   pip install .
   ```
   This will look at `pyproject.toml`, grab dependencies like `requests`, `pyfaidx`, etc. If you need external bio tools (`samtools`, NEAT, etc.), you must install them separately.

3. **Run**:
   ```
   bamboozler --help
   bamboozler download --species human --build hg38 ...
   ```

**Pros**  
- Easiest if you already have Python 3.10+ installed.  
- Minimizes overhead.

**Cons**  
- You must manually install external tools (samtools, etc.) and ensure they’re on PATH.  
- Potential for version conflicts with your local Python environment.

---

## Example Commands

### 1. Download & Slice a Reference

```
bamboozler download \
  --species human \
  --build hg38 \
  --chromosome 1 \
  --start 1000000 \
  --end 1001000 \
  --output human_chr1.fasta
```

### 2. Gene Annotation

```
bamboozler annotate \
  --annotation-source https://example.com/annotation.gff \
  --output local_annotation.gff \
  --feature gene \
  --gene BRCA1
```

### 3. Generate a BAM

```
bamboozler bam \
  --reference reference.fasta \
  --output-dir my_bam_output \
  --sample-name sample1 \
  --depth 1000 \
  --mutation-rate 0.01 \
  --signature-file cosmic_signature.tsv
```

### 4. Variant Insertion

```
bamboozler variant \
  --bam input.bam \
  --bai input.bai \
  --reference reference.fasta \
  --vcf variants.vcf \
  --output-dir variant_output \
  --output-name modified_sample \
  --allele-frequency 0.5 \
  --read-mix 0.5 \
  --variant-tool neat \
  --tool-param-file neat_params.yaml
```

---

## Troubleshooting

1. **Docker** complains about no permission?  
   - On Linux, ensure your user is in the `docker` group, or run with `sudo`.

2. **Conda** script fails to install to `~/miniconda`?  
   - Possibly your HPC admin disallows installing binaries in `$HOME`. Consult HPC docs or ask your admin.

3. **Missing external tools**?  
   - Tools like NEAT or VarSim might not be on PyPI or conda. Check your HPC environment or see the Docker approach, which can compile them from source.

4. **Python version conflict**?  
   - If using pip directly, confirm `python --version` is at least 3.10.

---

## License & Credits

**License**: [MIT License](./LICENSE)  
**Authors**: Your Name, 2025  
**Acknowledgements**: We rely on open-source tools like `pyfaidx`, `requests`, and many others from the Python bioinformatics community.

---

## In Conclusion

Pick **Docker**, **Conda**, or **pip**. Then run:

```
bamboozler --help
```

and have fun slicing references, generating BAM files, and injecting variants at your leisure! For questions or issues, open a GitHub Issue or contact us directly.

**Enjoy BamBoozler!** If a “4-month-old invertebrate” can handle it, so can you.
```
