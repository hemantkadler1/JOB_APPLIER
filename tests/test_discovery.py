"""
Unit tests for Job Discovery Orchestrator and Platform Modules.
"""

from discovery.orchestrator import DiscoveryOrchestrator

def test_discovery_orchestrator():
    orchestrator = DiscoveryOrchestrator()
    assert len(orchestrator.modules) == 7, "Expected all 7 discovery modules configured."

    jobs = orchestrator.run_all(
        keywords=["Java Developer", "Spring Boot"],
        locations=["Bengaluru", "Remote"]
    )

    assert len(jobs) > 0, "Expected jobs discovered from platform modules."
    for j in jobs:
        assert "title" in j
        assert "company_name" in j
        assert "url" in j
        assert "platform" in j
        assert "duplicate_hash" in j
