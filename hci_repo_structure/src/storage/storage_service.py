"""Storage service for managing storage pools and volumes."""


class StorageService:
    """Service for managing storage pools and volumes."""

    def __init__(self, max_pool_size=100):
        """Initialize StorageService.

        Args:
            max_pool_size: Maximum number of pools allowed (default: 100)
        """
        self.max_pool_size = max_pool_size
        self.pools = {}
        self.volumes = {}

    def create_pool(self, pool_id, size_gb):
        """Create a new storage pool.

        Args:
            pool_id: Unique identifier for the pool
            size_gb: Size of the pool in GB

        Returns:
            True if pool created successfully, False if max limit reached

        Raises:
            ValueError: If pool_id is empty or size_gb is not positive
        """
        if not pool_id or not pool_id.strip():
            raise ValueError("pool_id cannot be empty")
        if size_gb <= 0:
            raise ValueError("size_gb must be positive")

        if len(self.pools) >= self.max_pool_size:
            return False

        self.pools[pool_id] = {
            "size_gb": size_gb,
            "used_gb": 0,
            "status": "active"
        }
        return True

    def delete_pool(self, pool_id):
        """Delete a storage pool.

        Args:
            pool_id: Unique identifier for the pool

        Returns:
            True if pool deleted successfully, False if pool not found
        """
        if pool_id in self.pools:
            del self.pools[pool_id]
            return True
        return False

    def create_volume(self, volume_id, pool_id, size_gb):
        """Create a new volume in a storage pool.

        Args:
            volume_id: Unique identifier for the volume
            pool_id: ID of the pool to create volume in
            size_gb: Size of the volume in GB

        Returns:
            True if volume created successfully, False if insufficient space

        Raises:
            ValueError: If volume_id is empty or size_gb is not positive
            KeyError: If pool not found
        """
        if not volume_id or not volume_id.strip():
            raise ValueError("volume_id cannot be empty")
        if size_gb <= 0:
            raise ValueError("size_gb must be positive")

        if pool_id not in self.pools:
            raise KeyError(f"Pool {pool_id} not found")

        pool = self.pools[pool_id]
        available_space = pool["size_gb"] - pool["used_gb"]

        if size_gb > available_space:
            return False

        self.volumes[volume_id] = {
            "pool_id": pool_id,
            "size_gb": size_gb,
            "status": "available"
        }
        pool["used_gb"] += size_gb
        return True

    def get_pool_stats(self, pool_id):
        """Get statistics for a storage pool.

        Args:
            pool_id: Unique identifier for the pool

        Returns:
            Dictionary with pool statistics or empty dict if pool not found
        """
        if pool_id not in self.pools:
            return {}

        pool = self.pools[pool_id]
        total_size = pool["size_gb"]
        used_size = pool["used_gb"]
        available_size = total_size - used_size
        utilization = (used_size / total_size * 100) if total_size > 0 else 0

        return {
            "pool_id": pool_id,
            "total_size_gb": total_size,
            "used_gb": used_size,
            "available_gb": available_size,
            "utilization_percent": utilization,
            "status": pool["status"]
        }

    def list_volumes(self, pool_id=None):
        """List volumes, optionally filtered by pool.

        Args:
            pool_id: Optional pool ID to filter volumes

        Returns:
            List of volume IDs
        """
        if pool_id is None:
            return list(self.volumes.keys())

        return [
            vol_id for vol_id, vol_data in self.volumes.items()
            if vol_data["pool_id"] == pool_id
        ]
