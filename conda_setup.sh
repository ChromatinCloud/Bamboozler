#!/usr/bin/env bash
#
# conda_setup.sh
# 1. Checks if 'conda' is installed, else installs Miniconda (Linux x86_64).
# 2. Creates/updates the 'bamboozler-env' environment from 'environment.yml'.
# 3. Activates the environment (within this script) so we can...
# 4. Download the precompiled VarSim jar and create a 'varsim' wrapper.

set -e  # Exit on error

##############################################################################
# Step 1: Check for conda, or install Miniconda if absent
##############################################################################

ENV_NAME="bamboozler-env"
ENV_FILE="environment.yml"
MINICONDA_DIR="$HOME/miniconda"
MINICONDA_SCRIPT="Miniconda3-latest-Linux-x86_64.sh"
MINICONDA_URL="https://repo.anaconda.com/miniconda/${MINICONDA_SCRIPT}"

echo "[INFO] Checking for conda..."
if ! command -v conda &> /dev/null
then
    echo "[WARN] 'conda' not found. Attempting to install Miniconda to $MINICONDA_DIR."

    # Check OS quickly
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
      echo "[ERROR] This script only handles automatic Miniconda install on Linux x86_64."
      echo "        Please install conda manually for $OSTYPE."
      exit 1
    fi

    # Download Miniconda
    echo "[INFO] Downloading $MINICONDA_URL"
    curl -L -o "$MINICONDA_SCRIPT" "$MINICONDA_URL"

    echo "[INFO] Installing Miniconda to $MINICONDA_DIR (no user interaction)..."
    bash "$MINICONDA_SCRIPT" -b -p "$MINICONDA_DIR"

    rm -f "$MINICONDA_SCRIPT"

    export PATH="$MINICONDA_DIR/bin:$PATH"
    echo "[INFO] Miniconda installed. 'conda' should now be on PATH."
else
    echo "[INFO] 'conda' is already installed."
fi

# Confirm conda is available now
if ! command -v conda &> /dev/null
then
    echo "[ERROR] 'conda' still not found after Miniconda install. Aborting."
    exit 1
fi

##############################################################################
# Step 2: Create/Update the conda environment
##############################################################################

echo "[INFO] Creating or updating conda environment '${ENV_NAME}' from '${ENV_FILE}'..."
if [ ! -f "$ENV_FILE" ]; then
    echo "[ERROR] $ENV_FILE not found in the current directory."
    echo "        Make sure you run this script from the folder containing environment.yml."
    exit 1
fi

if ! conda env create -f "${ENV_FILE}" 2>/dev/null; then
    echo "[INFO] Environment creation failed, possibly it already exists."
    echo "[INFO] Attempting 'conda env update' instead..."
    conda env update -f "${ENV_FILE}" --prune
fi

##############################################################################
# Step 3: Activate the environment within the script
##############################################################################

# If you run ./conda_setup.sh (not 'source conda_setup.sh'), 
# the activation won't persist outside this script, but we 
# only need it active in the script so we can see $CONDA_PREFIX etc.

# In a subshell, we can do:
echo "[INFO] Activating environment '${ENV_NAME}' (within script)..."
(
  # This loads conda into the subshell. 
  # 'conda init' typically modifies your shell rc files, but 
  # we can manually do so by calling conda's 'activate' script.
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "${ENV_NAME}"

  ##############################################################################
  # Step 4: Download the precompiled VarSim jar + create wrapper
  ##############################################################################

  VARSIM_VERSION="0.8.4"  # Example placeholder
  VARSIM_URL="https://github.com/bioinform/varsim/releases/download/v${VARSIM_VERSION}/varsim.jar"
  BIN_DIR="${CONDA_PREFIX}/bin"

  echo "[INFO] Downloading VarSim jar from ${VARSIM_URL}"
  curl -L -o "${BIN_DIR}/varsim.jar" "${VARSIM_URL}"
  chmod +x "${BIN_DIR}/varsim.jar"

  echo "[INFO] Creating varsim wrapper script in ${BIN_DIR}/varsim"
  cat <<EOF > "${BIN_DIR}/varsim"
#!/usr/bin/env bash
java -jar "${BIN_DIR}/varsim.jar" "\$@"
EOF
  chmod +x "${BIN_DIR}/varsim"

  echo "[INFO] VarSim jar installed to ${BIN_DIR}. You can run 'varsim' when environment is activated."
)

##############################################################################
# Final message
##############################################################################

echo ""
echo "[INFO] Done. You can now use BamBoozler, NEAT, and VarSim in the '${ENV_NAME}' environment."
echo "      For example:"
echo "   conda activate ${ENV_NAME}"
echo "   bamboozler --help"
echo "   varsim --help"
echo ""
echo "[INFO] If you used ./conda_setup.sh, the environment isn't active in your current shell."
echo "      To activate it, run: conda activate ${ENV_NAME}"
echo ""

