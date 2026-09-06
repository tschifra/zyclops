#!/usr/bin/env python3
"""Compatibility entry point for the curated still-image pack builder."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("build-media-vault.py")), run_name="__main__")
