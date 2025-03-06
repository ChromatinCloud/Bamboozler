# Dockerfile for BamBoozler
# Provides a fully-contained environment with Python, 
# plus NEAT, BAM surgeon, and VarSim (precompiled jar).

FROM python:3.10-slim

# Install basic system packages often required by bioinformatics tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gcc \
    make \
    samtools \
    bwa \
    wgsim \
    openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy BamBoozler source code into the container
# (Assumes your BamBoozler repo, including pyproject.toml, is in the same folder as this Dockerfile)
COPY . /app

# Install BamBoozler from pyproject.toml
RUN pip install --upgrade pip
RUN pip install .

# ---- [BEGIN] NEAT Installation ----
RUN git clone https://github.com/ncsa/NEAT.git /tmp/NEAT && \
    cd /tmp/NEAT && \
    pip install .
# ---- [END] NEAT ----

# ---- [BEGIN] VarSim (Precompiled Jar) ----
# We'll download a jar from a VarSim release. Adjust URL/version as needed.
# e.g. version 0.8.4 (placeholder). Then put it somewhere on PATH.
RUN curl -L -o /usr/local/bin/varsim.jar \
    https://github.com/bioinform/varsim/releases/download/v0.8.4/varsim.jar && \
    chmod +x /usr/local/bin/varsim.jar

# Provide a small wrapper script so you can just type 'varsim'
RUN echo '#!/usr/bin/env bash\nexec java -jar /usr/local/bin/varsim.jar "$@"' > /usr/local/bin/varsim && \
    chmod +x /usr/local/bin/varsim
# ---- [END] VarSim ----

# Cleanup
RUN rm -rf /tmp/*

# Add /usr/local/bin to PATH just in case
ENV PATH="/usr/local/bin:${PATH}"

# Default command: start a shell inside the container
CMD ["/bin/bash"]

