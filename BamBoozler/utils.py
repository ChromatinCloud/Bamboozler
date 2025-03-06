import os
import subprocess
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

def ensure_tools_installed(tool_names):
    """
    Check if each named tool is on PATH.
    If not found, attempt naive 'pip install <tool>' or log an error.
    """
    for tool in tool_names:
        if not _is_tool_installed(tool):
            logger.warning("Tool '%s' not found. Attempting to install via pip ...", tool)
            try:
                subprocess.run(["pip", "install", tool], check=True)
                if _is_tool_installed(tool):
                    logger.info("Successfully installed %s.", tool)
                else:
                    logger.error("'%s' still not found after pip install.", tool)
            except Exception as e:
                logger.error("Could not install %s: %s", tool, e)
        else:
            logger.info("Tool '%s' is already installed.", tool)

def _is_tool_installed(tool):
    """
    Checks if the given tool is on PATH by using 'which' or Windows equivalent.
    """
    result = subprocess.run(["which", tool], capture_output=True, text=True)
    return (result.returncode == 0)

def parse_additional_params(raw_params):
    """
    Given a list of `--param value` pairs, convert them into a dictionary.
    For advanced usage in the CLI.
    """
    params_dict = {}
    i = 0
    while i < len(raw_params):
        key = raw_params[i].lstrip("-")
        if i + 1 < len(raw_params):
            val = raw_params[i+1]
            params_dict[key] = val
            i += 2
        else:
            i += 1

    if params_dict:
        logger.info("Parsed additional params: %s", params_dict)
    return params_dict

