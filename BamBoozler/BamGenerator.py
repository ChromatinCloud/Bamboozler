import os
import subprocess
import random
import shutil
from Bio import SeqIO

# If you have a centralized logger in BamBoozler/logging_config.py,
# you can import and use it like this:
# from BamBoozler.logging_config import get_logger
# logger = get_logger()
#
# For this standalone example, we'll just configure logging inline:
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

def _check_tool_in_path(tool_name: str) -> bool:
    """
    Check if a given tool (e.g. 'wgsim') is on the PATH by trying shutil.which().
    """
    return shutil.which(tool_name) is not None

class BAMGenerator:
    """
    A class to generate BAM files by simulating reads (using wgsim or similar),
    aligning them (with bwa), and converting/sorting them via samtools.
    """

    def __init__(self, reference_path: str, output_dir: str):
        """
        :param reference_path: Path to the reference FASTA
        :param output_dir: Directory where generated BAMs and intermediates will be placed
        """
        self.reference_path = reference_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        logger.info("Initialized BAMGenerator with reference=%s, output_dir=%s",
                    self.reference_path, self.output_dir)

        # Validate that our external tools are installed
        required_tools = ["wgsim", "bwa", "samtools"]
        for tool in required_tools:
            if not _check_tool_in_path(tool):
                logger.warning("Tool '%s' not found on PATH. This may cause runtime errors.", tool)

    def generate_bam(self, bam_name: str, depth: int, mutation_rate: float,
                     read_len: int = 100, seed: int = None) -> str:
        """
        Generate a new BAM file with specified depth and mutation rate using wgsim + bwa + samtools.

        :param bam_name: Base name of the output BAM file (without .bam)
        :param depth: Desired coverage or number of read pairs (depending on usage of wgsim)
        :param mutation_rate: Substitution rate for wgsim (-R param)
        :param read_len: Length of reads for wgsim
        :param seed: Optional random seed for reproducible simulation
        :return: The path to the sorted and indexed BAM file
        """
        logger.info("Generating BAM (name=%s, depth=%d, mutation_rate=%.4f, read_len=%d)...",
                    bam_name, depth, mutation_rate, read_len)
        if seed is not None:
            logger.info("Using random seed: %d", seed)

        # Prepare paths
        bam_path = os.path.join(self.output_dir, f"{bam_name}.bam")
        sam_path = os.path.join(self.output_dir, f"{bam_name}.sam")
        fq1_path = os.path.join(self.output_dir, f"{bam_name}_1.fq")
        fq2_path = os.path.join(self.output_dir, f"{bam_name}_2.fq")

        # 1) Simulate reads using wgsim
        wgsim_cmd = [
            "wgsim",
            "-N", str(depth),
            "-R", str(mutation_rate),
            "-1", str(read_len),
            "-2", str(read_len),
        ]
        # Add seed if given
        if seed is not None:
            wgsim_cmd.extend(["-S", str(seed)])

        wgsim_cmd.extend([
            self.reference_path,
            fq1_path,
            fq2_path
        ])
        logger.debug("Running wgsim command: %s", " ".join(wgsim_cmd))

        try:
            subprocess.run(wgsim_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("wgsim command failed: %s", e)
            raise RuntimeError("wgsim simulation error") from e

        # 2) Align reads to the reference genome using BWA
        bwa_cmd = [
            "bwa", "mem",
            self.reference_path,
            fq1_path,
            fq2_path
        ]
        logger.debug("Running bwa command: %s", " ".join(bwa_cmd))
        try:
            with open(sam_path, "w") as sam_out:
                subprocess.run(bwa_cmd, stdout=sam_out, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("bwa mem command failed: %s", e)
            raise RuntimeError("bwa alignment error") from e

        # 3) Convert SAM to BAM and sort
        try:
            # Convert SAM -> unsorted BAM
            with open(bam_path, "wb") as bam_out:
                subprocess.run(["samtools", "view", "-bS", sam_path],
                               stdout=bam_out, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("samtools view command failed: %s", e)
            raise RuntimeError("samtools view error") from e

        sorted_bam_path = os.path.join(self.output_dir, f"{bam_name}_sorted.bam")
        sort_cmd = ["samtools", "sort", bam_path, "-o", sorted_bam_path]
        logger.debug("Running samtools sort command: %s", " ".join(sort_cmd))
        try:
            subprocess.run(sort_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("samtools sort command failed: %s", e)
            raise RuntimeError("samtools sort error") from e

        # 4) Index the sorted BAM file
        index_cmd = ["samtools", "index", sorted_bam_path]
        logger.debug("Running samtools index command: %s", " ".join(index_cmd))
        try:
            subprocess.run(index_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("samtools index command failed: %s", e)
            raise RuntimeError("samtools index error") from e

        # 5) Clean up intermediate files
        for f in [sam_path, bam_path, fq1_path, fq2_path]:
            if os.path.exists(f):
                os.remove(f)

        logger.info("Successfully generated sorted, indexed BAM at %s", sorted_bam_path)
        return sorted_bam_path

if __name__ == "__main__":
    # Example usage
    generator = BAMGenerator(reference_path="reference.fasta", output_dir="bam_output")
    # Provide a numeric seed for reproducibility if desired
    bam_path = generator.generate_bam(bam_name="sample", depth=1000, mutation_rate=0.01, seed=42)
    print(f"Generated BAM file: {bam_path}")

