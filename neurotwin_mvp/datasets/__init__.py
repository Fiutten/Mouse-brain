"""Optional real-data adapters.

Adapters in this package must not be imported by the core MVP unless explicitly
requested. This keeps the synthetic/test pipeline usable without heavy external
neuroscience dependencies.
"""

from .allen import AllenMetadataSmokeResult, AllenVisualBehaviorNeuropixelsLoader
from .ibl import IBLBrainwideMapLoader

__all__ = [
    "AllenVisualBehaviorNeuropixelsLoader",
    "AllenMetadataSmokeResult",
    "IBLBrainwideMapLoader",
]
