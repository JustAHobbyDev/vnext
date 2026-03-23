"""Benchmark evaluation primitives for vNext."""

from vnext.benchmarks.loader import LoadedCase, load_case_inputs
from vnext.benchmarks.photonics import BenchmarkRun, build_photonics_benchmark

__all__ = ["BenchmarkRun", "LoadedCase", "build_photonics_benchmark", "load_case_inputs"]
