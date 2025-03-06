import os
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)


class GenomeAnnotator:
    """
    A class for retrieving and subsetting gene annotation files (e.g., GFF or GTF).
    """

    def __init__(self, annotation_source: str):
        """
        :param annotation_source: URL or local path to a GFF/GTF annotation file
        """
        self.annotation_source = annotation_source
        logger.info("Initialized GenomeAnnotator with source=%s", annotation_source)

    def retrieve_annotation(self, output: str) -> None:
        """
        Retrieves a gene annotation file from a URL (or local path) and saves to `output`.
        """
        if os.path.isfile(self.annotation_source):
            logger.info("Local annotation file found at %s, copying to %s", self.annotation_source, output)
            with open(self.annotation_source, "rb") as src, open(output, "wb") as dst:
                dst.write(src.read())
        else:
            logger.info("Downloading annotation from %s to %s", self.annotation_source, output)
            r = requests.get(self.annotation_source)
            if r.status_code != 200:
                msg = f"Failed to download annotation (status={r.status_code}): {self.annotation_source}"
                logger.error(msg)
                raise RuntimeError(msg)
            with open(output, "wb") as f:
                f.write(r.content)

        logger.info("Annotation saved to %s", output)

    def subset_annotation(self,
                          input_file: str,
                          output_file: str,
                          feature: str = None,
                          gene_name: str = None) -> None:
        """
        Filters the annotation by feature type (e.g. 'gene') and gene name if provided.
        Writes the subsetted data to `output_file`.

        :param input_file: Path to the existing annotation file (e.g. GFF or GTF)
        :param output_file: Where the filtered lines go
        :param feature: e.g. "gene", "exon", etc. Case-insensitive
        :param gene_name: e.g. "BRCA1" to match an attribute in the 9th column of GFF
        """
        if not os.path.isfile(input_file):
            msg = f"Input annotation file {input_file} not found."
            logger.error(msg)
            raise FileNotFoundError(msg)

        lines_kept = 0
        with open(input_file, "r") as fin, open(output_file, "w") as fout:
            for line in fin:
                if line.startswith("#"):
                    fout.write(line)
                    continue

                cols = line.strip().split("\t")
                if len(cols) < 9:
                    continue

                feature_type = cols[2]
                attributes = cols[8]

                # Filter by feature if given
                if feature and feature_type.lower() != feature.lower():
                    continue

                # Filter by gene_name if given
                if gene_name and gene_name.lower() not in attributes.lower():
                    continue

                fout.write(line)
                lines_kept += 1

        logger.info("Subset annotation saved to %s (kept %d lines)", output_file, lines_kept)


if __name__ == "__main__":
    # Example usage
    annotator = GenomeAnnotator("https://example.com/annotation.gff")
    annotator.retrieve_annotation("local_annotation.gff")
    annotator.subset_annotation("local_annotation.gff", "filtered.gff", feature="gene", gene_name="BRCA1")
    print("Filtered annotation saved to filtered.gff")

