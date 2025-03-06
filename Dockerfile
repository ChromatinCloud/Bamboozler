# Use Miniconda as the base image
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy all your project files into /app (including environment.yml, pyproject.toml, etc.)
COPY . /app

# Install mamba in base environment for faster env creation
RUN conda install -n base -c conda-forge mamba

# Create the conda environment from environment.yml
RUN mamba env create -f /app/environment.yml

# Ensure all subsequent commands run inside the bamboozler_env environment
SHELL ["conda", "run", "-n", "bamboozler_env", "/bin/bash", "-c"]

# Install VarSim from GitHub using Maven
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    default-jre-headless \
    maven && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --recurse-submodules https://github.com/bioinform/varsim.git /opt/varsim && \
    cd /opt/varsim && \
    mvn clean package -Dmaven.compiler.source=1.8 -Dmaven.compiler.target=1.8

# Set the entrypoint for the container to launch a shell by default
ENTRYPOINT ["/bin/bash"]

