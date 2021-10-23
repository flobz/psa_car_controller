import sys
import traceback

import pkg_resources
from pathlib import Path

from mylogger import logger
class TestRequirements:
    """Test availability of required packages."""

    def __init__(self, requirement_path):
        self.requirement_path = Path(requirement_path)

    def test_requirements(self):
        """Test that each required package is available."""
        requirements = pkg_resources.parse_requirements(self.requirement_path.open())
        missing_requirement = False
        for requirement in requirements:
            requirement = str(requirement)
            try:
                pkg_resources.require(requirement)
            except pkg_resources.VersionConflict:
                logger.debug(traceback.format_exc())
                logger.error("You need to install or update some dependencies: pip3 install -U %s", requirement)
                missing_requirement=True
        if missing_requirement:
            sys.exit(10)