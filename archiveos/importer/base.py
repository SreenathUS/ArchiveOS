from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple

from archiveos.types import FileRecord


class Importer(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def scan(self, source_root: Path) -> Tuple[List[FileRecord], Dict[Tuple[str, str], List[FileRecord]]]:
        raise NotImplementedError

    @abstractmethod
    def verify_source(self, source_root: Path) -> None:
        raise NotImplementedError
