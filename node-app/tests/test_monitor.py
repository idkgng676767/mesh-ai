from agent import monitor


def test_monitor_metrics():
    assert monitor.get_ram_gb() > 0
    assert monitor.get_cpu_freq_ghz() >= 0
    utilization = monitor.get_utilization_multiplier()
    assert 0.1 <= utilization <= 1.0
