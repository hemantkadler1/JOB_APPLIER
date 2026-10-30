"""
Discovery Orchestrator.
Coordinates concurrent execution of all 7 discovery modules:
- Naukri
- LinkedIn
- Indeed
- Wellfound
- Instahyre
- Cutshort
- Official Career Pages
"""

from typing import List, Dict, Any
from discovery.naukri import NaukriDiscovery
from discovery.linkedin import LinkedInDiscovery
from discovery.indeed import IndeedDiscovery
from discovery.wellfound import WellfoundDiscovery
from discovery.instahyre import InstahyreDiscovery
from discovery.cutshort import CutshortDiscovery
from discovery.career_pages import CareerPagesDiscovery
from config.settings import get_logger

logger = get_logger(__name__)

class DiscoveryOrchestrator:
    """Manages all discovery channels."""

    def __init__(self):
        self.modules = [
            NaukriDiscovery(),
            LinkedInDiscovery(),
            IndeedDiscovery(),
            WellfoundDiscovery(),
            InstahyreDiscovery(),
            CutshortDiscovery(),
            CareerPagesDiscovery(),
        ]

    def run_all(self, keywords: List[str], locations: List[str]) -> List[Dict[str, Any]]:
        """Run all discovery modules and pool discovered jobs."""
        all_jobs: List[Dict[str, Any]] = []
        logger.info(f"Initiating job discovery across {len(self.modules)} channels...")

        for module in self.modules:
            try:
                platform_jobs = module.fetch_jobs(keywords, locations)
                all_jobs.extend(platform_jobs)
                logger.info(f"[{module.platform_name}] returned {len(platform_jobs)} jobs.")
            except Exception as e:
                logger.error(f"Error executing discovery on {module.platform_name}: {e}")

        logger.info(f"Total discovered jobs across all platforms: {len(all_jobs)}")
        return all_jobs
