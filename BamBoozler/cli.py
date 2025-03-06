import argparse
import sys
import logging
import os

from BamBoozler.ReferenceDownloader import ReferenceDownloader
from BamBoozler.GenomeAnnotator import GenomeAnnotator
from BamBoozler.BamGenerator import BAMGenerator
from BamBoozler.VariantSimulator import VariantSimulator
from BamBoozler.utils import ensure_tools_installed, parse_additional_params

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

def main():
    parser = argparse.ArgumentParser(
        description="BamBoozler: Reference Genome Processing, BAM Generation, Variant Simulation"
    )
    subparsers = parser.add_subparsers(dest="command")

    # install-tools
    install_parser = subparsers.add_parser("install-tools", help="Install external tools in the environment")
    install_parser.add_argument("tools", nargs="*", help="List of tool names to install (e.g. neat, varsim, bamcake)")

    # download
    download_parser = subparsers.add_parser("download", help="Download & slice reference genome")
    download_parser.add_argument("--species", required=True)
    download_parser.add_argument("--build", required=True)
    download_parser.add_argument("--chromosome", required=True)
    download_parser.add_argument("--start", type=int, default=1)
    download_parser.add_argument("--end", type=int, default=0)
    download_parser.add_argument("--output", required=True)
    download_parser.add_argument("--force-download", action="store_true",
                                 help="Redownload the reference even if local copy is present")

    # annotate
    annotate_parser = subparsers.add_parser("annotate", help="Retrieve and/or subset gene annotation files")
    annotate_parser.add_argument("--annotation-source", required=True)
    annotate_parser.add_argument("--output", required=True)
    annotate_parser.add_argument("--feature", default=None)
    annotate_parser.add_argument("--gene", default=None)

    # bam
    bam_parser = subparsers.add_parser("bam", help="Generate a synthetic BAM file")
    bam_parser.add_argument("--reference", required=True)
    bam_parser.add_argument("--output-dir", required=True)
    bam_parser.add_argument("--sample-name", default="sample")
    bam_parser.add_argument("--depth", type=int, default=1000)
    bam_parser.add_argument("--mutation-rate", type=float, default=0.01)
    bam_parser.add_argument("--signature-file", default=None)
    bam_parser.add_argument("--other-params", nargs="*", default=None,
                            help="Additional key-value pairs, e.g. --other-params --param1 val1 --param2 val2")
    bam_parser.add_argument("--read-len", type=int, default=100,
                            help="Read length for wgsim simulation (defaults to 100)")
    bam_parser.add_argument("--seed", type=int, default=None,
                            help="Optional random seed for reproducible wgsim runs")

    # variant
    variant_parser = subparsers.add_parser("variant", help="Edit variants in an existing BAM")
    variant_parser.add_argument("--bam", required=True)
    variant_parser.add_argument("--bai", required=True)
    variant_parser.add_argument("--reference", required=True)
    variant_parser.add_argument("--vcf", required=True)
    variant_parser.add_argument("--output-dir", required=True)
    variant_parser.add_argument("--output-name", required=True)
    variant_parser.add_argument("--allele-frequency", type=float, default=0.5)
    variant_parser.add_argument("--read-mix", type=float, default=0.5)
    variant_parser.add_argument("--variant-tool", default=None,
                            help="Specify which external tool to use (neat, varsim, bamsurgeon) or leave empty for internal logic.")
    variant_parser.add_argument("--tool-param-file", default=None,
                                help="Path to a YAML file containing tool-specific parameters.")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    logger.info("Command requested: %s", args.command)

    try:
        if args.command == "install-tools":
            if not args.tools:
                logger.info("No tools specified. Example usage: bamboozler install-tools neat varsim bamcake")
            else:
                ensure_tools_installed(args.tools)

        elif args.command == "download":
            logger.info("Downloading reference: species=%s build=%s chr=%s start=%d end=%d output=%s force=%s",
                        args.species, args.build, args.chromosome, args.start, args.end, args.output, args.force_download)
            rd = ReferenceDownloader(
                species=args.species,
                build=args.build,
                chromosome=args.chromosome,
                force_download=args.force_download
            )
            rd.download_and_slice(start=args.start, end=args.end, output=args.output)

        elif args.command == "annotate":
            logger.info("Annotation source=%s, output=%s, feature=%s, gene=%s",
                        args.annotation_source, args.output, args.feature, args.gene)
            annotator = GenomeAnnotator(args.annotation_source)
            annotator.retrieve_annotation(args.output)

            if args.feature or args.gene:
                tmp_output = args.output + ".tmp"
                os.rename(args.output, tmp_output)
                annotator.subset_annotation(
                    input_file=tmp_output,
                    output_file=args.output,
                    feature=args.feature,
                    gene_name=args.gene
                )
                os.remove(tmp_output)

        elif args.command == "bam":
            logger.info("Generating BAM: reference=%s, output_dir=%s, sample_name=%s, depth=%d, mutation_rate=%.4f",
                        args.reference, args.output_dir, args.sample_name, args.depth, args.mutation_rate)
            other_params = None
            if args.other_params:
                other_params = parse_additional_params(args.other_params)

            bam_gen = BAMGenerator(reference_path=args.reference, output_dir=args.output_dir)
            sorted_bam_path = bam_gen.generate_bam(
                bam_name=args.sample_name,
                depth=args.depth,
                mutation_rate=args.mutation_rate,
                read_len=args.read_len,
                seed=args.seed
            )
            logger.info("Generated BAM at %s", sorted_bam_path)

        elif args.command == "variant":
            logger.info("Adding variants: bam=%s bai=%s ref=%s vcf=%s tool=%s",
                        args.bam, args.bai, args.reference, args.vcf, args.variant_tool)

            vsim = VariantSimulator(
                bam=args.bam,
                bai=args.bai,
                reference=args.reference,
                vcf=args.vcf,
                output_dir=args.output_dir,
                output_name=args.output_name,
                allele_freq=args.allele_frequency,
                read_mix=args.read_mix,
                tool_param_file=args.tool_param_file
            )
            vsim.run(variant_tool=args.variant_tool)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.exception("An error occurred: %s", e)
        sys.exit(1)

