"""Tests for compute_embeddings helpers.

Covers the GPU-memory → batch-size heuristic.  The encode_narratives path
itself requires a real model load + (optionally) CUDA, so it's exercised
end-to-end via skol's bin/embed_treatments rather than unit-tested here.
"""

from . import compute_embeddings


_GB = 1024 ** 3


class TestRecommendBatchSizeFromGpuMemory:
    """Tier table for choosing a default batch_size from total GPU memory."""

    def test_tiny_gpu_falls_back_to_64(self):
        # 4 GB devices (e.g. older laptops) — keep the pre-existing default.
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(4 * _GB) == 64

    def test_8_gb_class(self):
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(8 * _GB) == 128
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(10 * _GB) == 128

    def test_16_gb_class(self):
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(16 * _GB) == 256

    def test_24_gb_class(self):
        # The "dev box" tier — 3090 / 4090 / A5000.
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(24 * _GB) == 512

    def test_40_gb_class(self):
        # A100-40 / A6000.
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(40 * _GB) == 1024

    def test_80_gb_class(self):
        # A100-80 / H100.
        assert compute_embeddings.recommend_batch_size_from_gpu_memory(80 * _GB) == 2048

    def test_monotonic_non_decreasing(self):
        """A larger GPU never picks a smaller batch size than a smaller one."""
        prev = 0
        for gb in (1, 4, 6, 8, 12, 16, 20, 24, 28, 40, 44, 64, 80, 128):
            val = compute_embeddings.recommend_batch_size_from_gpu_memory(gb * _GB)
            assert val >= prev, f"regression at {gb} GB: {val} < {prev}"
            prev = val

    def test_returns_power_of_two(self):
        """Result is always a power of two — keeps SBERT happy and pairs
        nicely with most GPU warp sizes."""
        for gb in (1, 6, 8, 12, 16, 20, 24, 28, 40, 44, 64, 80, 128):
            val = compute_embeddings.recommend_batch_size_from_gpu_memory(gb * _GB)
            assert val & (val - 1) == 0, f"{val} is not a power of two"


class TestEmbeddingsComputerBatchSizeParam:
    """The new constructor parameter must round-trip onto the instance."""

    def test_default_is_none(self):
        ec = compute_embeddings.EmbeddingsComputer(idir="/tmp")
        assert ec.batch_size is None

    def test_explicit_value_kept(self):
        ec = compute_embeddings.EmbeddingsComputer(idir="/tmp", batch_size=128)
        assert ec.batch_size == 128
