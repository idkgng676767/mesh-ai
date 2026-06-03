from __future__ import annotations

import psutil

try:
    import GPUtil  # type: ignore
except Exception:  # pragma: no cover
    GPUtil = None


def get_cpu_freq_ghz() -> float:
    freq = psutil.cpu_freq()
    if not freq:
        return 0.0
    return round(freq.current / 1000.0, 2)


def get_ram_gb() -> float:
    return round(psutil.virtual_memory().total / (1024 ** 3), 2)


def get_gpu_vram_gb() -> float:
    if not GPUtil:
        return 0.0
    gpus = GPUtil.getGPUs()
    if not gpus:
        return 0.0
    return round(max(gpu.memoryTotal for gpu in gpus) / 1024.0, 2)


def get_utilization_multiplier() -> float:
    cpu_usage = psutil.cpu_percent(interval=0.1)
    gpu_usage = 0.0
    if GPUtil:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = max(gpu.load for gpu in gpus) * 100
    busy = max(cpu_usage, gpu_usage)
    utilization = max(0.1, min(1.0, 1 - busy / 100))
    return round(utilization, 2)
