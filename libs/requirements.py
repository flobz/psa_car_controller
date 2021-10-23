import pkg_resources
from pathlib import Path


class TestRequirements:
    """Test availability of required packages."""

    def __init__(self, requirement_path):
        self.requirement_path = Path(requirement_path)

    def test_requirements(self):
        """Test that each required package is available."""
        # Ref: https://stackoverflow.com/a/45474387/
        requirements = pkg_resources.parse_requirements(self.requirement_path.open())
        for requirement in requirements:
            requirement = str(requirement)
            pkg_resources.require(requirement)
