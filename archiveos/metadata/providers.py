from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterable


Metadata = Dict[str, object]


class MetadataProvider(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract(self, files: Iterable[Path]) -> Dict[str, Metadata]:
        """Return mapping of absolute path string -> metadata dict."""
        raise NotImplementedError
