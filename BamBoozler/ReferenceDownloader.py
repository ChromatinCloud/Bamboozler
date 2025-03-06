import os
import logging
import requests
from pyfaidx import Fasta, FetchError

# If you have a centralized logger, import and use it:
# from BamBoozler.logging_config import get_logger
# logger = get_logger()
#
# For this standalone example, we'll configure inline:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

# You can extend these mappings as needed:
ENSEMBL_SPECIES_MAP = {
    "human": "homo_sapiens",
    # "mouse": "mus_musculus",
}
ENSEMBL_BUILD_MAP = {
    "hg38": "GRCh38",
    "hg19": "GRCh37",
}

class ReferenceDownloader:
    """
    A class to handle downloading and slicing reference genome FASTAs from Ensembl (or local copies).
    Uses pyfaidx for indexing and subsetting the final region.
    """

    def __init__(self, species: str, build: str, chromosome: str, force_download: bool = False):
        """
        :param species: e.g. "human"
        :param build: e.g. "hg38" (maps internally to "GRCh38")
        :param chromosome: e.g. "1" or "chr1"
        :param force_download: If True, redownload the FASTA even if a local copy exists
        """
        self.species = species.lower()
        self.build = build.lower()
        self.chromosome = chromosome
        self.force_download = force_download

        # Construct local names from mappings
        self.ensembl_species = ENSEMBL_SPECIES_MAP.get(self.species, self.species)
        self.ensembl_build = ENSEMBL_BUILD_MAP.get(self.build, self.build)
        # For user convenience, remove 'chr' if present
        self.chr_clean = self.chromosome.replace("chr", "")

        # Build the local .fa.gz filename
        capitalized_species = self.ensembl_species.replace("_", " ").title().replace(" ", "_")
        self.local_fasta_gz = f"{capitalized_species}.{self.ensembl_build}.dna.chromosome.{self.chr_clean}.fa.gz"

        logger.info("Initialized ReferenceDownloader: species=%s, build=%s, chromosome=%s, force_download=%s",
                    self.species, self.build, self.chromosome, self.force_download)

    def download_and_slice(self, start: int, end: int, output: str) -> None:
        """
        Downloads (if needed) the compressed FASTA for species/build/chromosome from Ensembl,
        indexes it via pyfaidx, then slices out [start:end] (1-based, inclusive) and writes
        the subsequence to 'output'.

        :param start: 1-based start coordinate
        :param end: 1-based end coordinate
        :param output: Output FASTA filename
        :raises RuntimeError: If the chromosome file cannot be downloaded or slicing fails
        """
        # 1) Build the remote URL
        try:
            fasta_url = self._resolve_ensembl_url()
        except Exception as e:
            logger.error("Failed to construct Ensembl URL for species=%s build=%s chromosome=%s: %s",
                         self.species, self.build, self.chromosome, e)
            raise

        # 2) Download if needed
        if self.force_download or not os.path.exists(self.local_fasta_gz):
            logger.info("Fetching chromosome FASTA from Ensembl: %s", fasta_url)
            try:
                self._download_file(fasta_url, self.local_fasta_gz)
            except Exception as e:
                msg = f"Failed downloading chromosome from Ensembl: {e}"
                logger.error(msg)
                raise RuntimeError(msg) from e
        else:
            logger.info("Local copy of %s found. Skipping download.", self.local_fasta_gz)

        # 3) Open & index with pyfaidx, slice region
        logger.info("Indexing %s via pyfaidx...", self.local_fasta_gz)
        try:
            fa = Fasta(self.local_fasta_gz, as_raw=True, one_based_attributes=True)
        except Exception as e:
            msg = f"Could not index or parse {self.local_fasta_gz}: {e}"
            logger.error(msg)
            raise RuntimeError(msg) from e

        # Attempt slicing with or without "chr" prefix
        target_id_options = [self.chr_clean, f"chr{self.chr_clean}"]
        seq_slice = None
        for tid in target_id_options:
            if tid in fa:
                try:
                    seq_slice = fa[tid][start:end]  # 1-based slicing
                    break
                except FetchError:
                    logger.warning("Out-of-range slice attempt: tid=%s start=%d end=%d", tid, start, end)
                    pass

        if seq_slice is None or len(seq_slice) == 0:
            msg = (f"Could not slice region {self.chromosome}:{start}-{end} from {self.local_fasta_gz}. "
                   "Check chromosome naming or coordinate range.")
            logger.error(msg)
            raise RuntimeError(msg)

        # 4) Write out the slice
        with open(output, "w") as out_f:
            header = f">{self.chromosome}:{start}-{end} ({self.species},{self.build})"
            out_f.write(header + "\n")
            out_f.write(str(seq_slice) + "\n")

        logger.info("Wrote sliced FASTA to %s [length=%d bp]", output, len(seq_slice))

    def _resolve_ensembl_url(self) -> str:
        """
        Constructs the Ensembl URL for the compressed FASTA of the given chromosome.

        Example:
          https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz
        """
        capitalized_species = self.ensembl_species.replace("_", " ").title().replace(" ", "_")
        filename = f"{capitalized_species}.{self.ensembl_build}.dna.chromosome.{self.chr_clean}.fa.gz"
        url = f"https://ftp.ensembl.org/pub/current_fasta/{self.ensembl_species}/dna/{filename}"
        return url

    def _download_file(self, url: str, local_path: str, chunk_size: int = 1024 * 1024) -> None:
        """
        Downloads a file from the given URL in chunks.
        Raises RuntimeError if status_code != 200 or if any issue arises.
        """
        logger.info("Downloading from %s", url)
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code} fetching {url}")

        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        logger.info("Downloaded file -> %s (%.2f MB)", local_path, os.path.getsize(local_path)/1e6)


if __name__ == "__main__":
    # Example usage
    downloader = ReferenceDownloader(species="human", build="hg38", chromosome="1", force_download=False)
    downloader.download_and_slice(start=1000000, end=1001000, output="slice.fasta")
    print("Sliced reference saved to slice.fasta")

