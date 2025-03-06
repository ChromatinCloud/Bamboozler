import os
import subprocess
import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

class VariantSimulator:
    """
    Class for adding or editing variants in an existing BAM file.
    Supports external tools NEAT, VarSim, and BamSurgeon.
    """

    def __init__(self, 
                 bam: str,
                 bai: str,
                 reference: str,
                 vcf: str,
                 output_dir: str,
                 output_name: str,
                 allele_freq: float = 0.5,
                 read_mix: float = 0.5,
                 tool_param_file: str = None):
        """
        :param bam: Path to input BAM
        :param bai: Path to the BAM index file
        :param reference: Path to reference FASTA
        :param vcf: Path to a VCF describing variants to introduce
        :param output_dir: Directory to store the modified BAM
        :param output_name: Output BAM name (no .bam extension)
        :param allele_freq: Desired allele frequency
        :param read_mix: Ratio of forward/reverse reads carrying the variant
        :param tool_param_file: Optional path to a YAML file specifying extra parameters for external tools
        """
        self.bam = bam
        self.bai = bai
        self.reference = reference
        self.vcf = vcf
        self.output_dir = output_dir
        self.output_name = output_name
        self.allele_freq = allele_freq
        self.read_mix = read_mix
        self.tool_param_file = tool_param_file

        os.makedirs(self.output_dir, exist_ok=True)

        # Load extra params from YAML if provided
        self.extra_params = {}
        if self.tool_param_file and os.path.isfile(self.tool_param_file):
            logger.info("Loading extra tool parameters from %s", self.tool_param_file)
            with open(self.tool_param_file, "r") as f:
                self.extra_params = yaml.safe_load(f) or {}

        logger.info("VariantSimulator initialized with bam=%s, reference=%s, vcf=%s, output_dir=%s",
                    bam, reference, vcf, output_dir)

    def run(self, variant_tool: str = None):
        """
        Entry point for adding/editing variants. If variant_tool is None,
        we use an internal placeholder approach. Otherwise, we invoke NEAT, VarSim, or BamSurgeon.
        """
        logger.info("Starting variant addition with tool=%s", variant_tool or "internal")
        logger.info("bam=%s, bai=%s, ref=%s, vcf=%s, out_name=%s",
                    self.bam, self.bai, self.reference, self.vcf, self.output_name)
        logger.info("allele_freq=%.2f, read_mix=%.2f", self.allele_freq, self.read_mix)

        if variant_tool is None:
            logger.warning("No external tool specified. Using internal variant insertion logic.")
            self._internal_variant_insertion()
        elif variant_tool.lower() in ["neat", "varsim", "bamsurgeon"]:
            self._run_external_variant_tool(variant_tool.lower())
        else:
            logger.error("Unrecognized variant tool '%s'. Aborting.", variant_tool)

    def _internal_variant_insertion(self):
        """
        Placeholder for a pure-Python approach to introducing variants into an existing BAM.
        """
        out_bam = os.path.join(self.output_dir, f"{self.output_name}.bam")
        logger.info("Using internal variant insertion. Output BAM: %s", out_bam)
        with open(out_bam, "w") as f:
            f.write("Placeholder for internal variant insertion logic.\n")
        logger.info("Internal variant insertion complete (placeholder).")

    def _run_external_variant_tool(self, tool: str):
        """
        Run an external variant editing tool (NEAT, VarSim, or BamSurgeon).
        """
        logger.info("Running external tool: %s with extra_params=%s", tool, self.extra_params)
        if tool == "neat":
            self._run_neat()
        elif tool == "varsim":
            self._run_varsim()
        elif tool == "bamsurgeon":
            self._run_bamsurgeon()

    def _run_bamsurgeon(self):
        """
        Executes BamSurgeon with conditionally included parameters.
        """
        cmd = [
            "python3", "-O", "/opt/bamsurgeon/bin/addsnv.py",
            "-v", self.vcf,
            "-f", self.bam,
            "-r", self.reference,
            "-o", os.path.join(self.output_dir, f"{self.output_name}.bam")
        ]

        # Optional parameters
        af = self.extra_params.get("allele_freq", self.allele_freq)
        if af:
            cmd.extend(["--af", str(af)])

        seed = self.extra_params.get("seed")
        if seed:
            cmd.extend(["--seed", str(seed)])

        aligner = self.extra_params.get("aligner", "bwa")
        cmd.extend(["--aligner", aligner])

        inslib = self.extra_params.get("inslib")
        if inslib:
            cmd.extend(["--inslib", inslib])

        keepsecondary = self.extra_params.get("keepsecondary", False)
        if keepsecondary:
            cmd.append("--keepsecondary")

        logger.info("Running BamSurgeon command: %s", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            logger.error("'addsnv.py' from BamSurgeon not found. Check installation.")
        except subprocess.CalledProcessError as e:
            logger.error("BamSurgeon command failed: %s", e)
        else:
            logger.info("BamSurgeon variant insertion complete.")

    def _run_neat(self):
        """
        Executes NEAT with conditionally included parameters.
        """
        cmd = [
            "neat-genreads.py",
            "-R", self.reference,
            "-o", os.path.join(self.output_dir, self.output_name)
        ]

        if self.vcf:
            cmd.extend(["-v", self.vcf])

        coverage = self.extra_params.get("coverage")
        if coverage:
            cmd.extend(["-c", str(coverage)])

        read_len = self.extra_params.get("read_length")
        if read_len:
            cmd.extend(["-r", str(read_len)])

        error_model = self.extra_params.get("error_model")
        if error_model:
            cmd.extend(["--error", error_model])

        vaf = self.extra_params.get("vaf")
        if vaf:
            cmd.extend(["--min_vaf", str(vaf), "--max_vaf", str(vaf)])

        if self.extra_params.get("paired_end"):
            cmd.append("--pe")

        logger.info("Running NEAT command: %s", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            logger.error("'neat-genreads.py' not found. Check your PATH or environment.")
        except subprocess.CalledProcessError as e:
            logger.error("NEAT command failed: %s", e)
        else:
            logger.info("NEAT variant insertion complete.")

    def _run_varsim(self):
        """
        Executes VarSim with conditionally included parameters.
        """
        cmd = [
            "varsim",
            "simulate",
            "--reference", self.reference,
            "--out_dir", self.output_dir,
        ]

        if self.vcf:
            cmd.extend(["--vcfs", self.vcf])

        coverage = self.extra_params.get("coverage")
        if coverage:
            cmd.extend(["--coverage", str(coverage)])

        logger.info("Running VarSim command: %s", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            logger.error("'varsim' not found. Check your PATH or environment.")
        except subprocess.CalledProcessError as e:
            logger.error("VarSim command failed: %s", e)
        else:
            logger.info("VarSim simulation complete.")

