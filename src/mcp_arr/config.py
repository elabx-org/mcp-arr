"""Configuration from environment variables."""

import os
from dataclasses import dataclass


@dataclass
class InstanceConfig:
    """Configuration for a single arr instance."""

    name: str
    url: str
    api_key: str
    instance_type: str  # "sonarr" or "radarr"


class Config:
    """Multi-instance arr configuration from environment variables.

    Instances are discovered by scanning for ARR_{NAME}_URL environment
    variables. Each instance also requires ARR_{NAME}_KEY. The type
    ARR_{NAME}_TYPE defaults to "sonarr" if not set.

    Example:
        ARR_SONARR_URL=http://sonarr:8989
        ARR_SONARR_KEY=abc123
        ARR_SONARR_TYPE=sonarr   # optional, defaults to sonarr

        ARR_RADARR_URL=http://radarr:7878
        ARR_RADARR_KEY=ghi789
        ARR_RADARR_TYPE=radarr
    """

    @classmethod
    def get_instances(cls) -> dict[str, InstanceConfig]:
        """Auto-discover instances from ARR_*_URL environment variables.

        Returns:
            Dict mapping lowercase instance name to InstanceConfig.
            E.g., {"sonarr": InstanceConfig(...), "radarr": InstanceConfig(...)}
        """
        instances: dict[str, InstanceConfig] = {}

        for key, value in os.environ.items():
            if not key.startswith("ARR_") or not key.endswith("_URL"):
                continue
            # Extract the NAME part: ARR_{NAME}_URL
            name = key[4:-4]  # strip "ARR_" prefix and "_URL" suffix
            if not name:
                continue

            url = value.strip()
            if not url:
                continue

            api_key = os.environ.get(f"ARR_{name}_KEY", "").strip()
            if not api_key:
                continue

            instance_type = os.environ.get(f"ARR_{name}_TYPE", "sonarr").strip().lower()
            if instance_type not in ("sonarr", "radarr"):
                instance_type = "sonarr"

            instances[name.lower()] = InstanceConfig(
                name=name.lower(),
                url=url,
                api_key=api_key,
                instance_type=instance_type,
            )

        return instances

    @classmethod
    def validate(cls) -> None:
        """Raise ValueError if no instances are configured."""
        instances = cls.get_instances()
        if not instances:
            raise ValueError(
                "No arr instances configured. "
                "Set ARR_{NAME}_URL and ARR_{NAME}_KEY environment variables. "
                "Example: ARR_SONARR_URL=http://sonarr:8989, ARR_SONARR_KEY=your_api_key"
            )
