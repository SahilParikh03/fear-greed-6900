"""
Base fetcher interface for all data sources.

This module defines the abstract base class that all fetchers must implement
to ensure a consistent interface across different data sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseFetcher(ABC):
    """
    Abstract base class for all data fetchers.

    All fetchers must implement the fetch() method to retrieve data from their
    respective sources. This ensures consistency and makes it easy to add new
    data sources without changing the rest of the system.
    """

    @abstractmethod
    async def fetch(self) -> Dict[str, Any]:
        """
        Fetch raw data from the source.

        Returns:
            Dict containing the raw data from the source. The structure will vary
            by fetcher but should always be a dictionary.

        Raises:
            Exception: Any errors during fetching should be raised with descriptive messages.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the data source is available and accessible.

        Returns:
            bool: True if the source is healthy, False otherwise.
        """
        pass
