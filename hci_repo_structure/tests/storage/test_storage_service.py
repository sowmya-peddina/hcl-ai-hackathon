"""Unit tests for StorageService."""

import pytest
from hci_repo_structure.src.storage.storage_service import StorageService


class TestStorageServiceInitialization:
    """Test StorageService initialization."""

    def test_init_default_max_pool_size(self):
        """Test default max_pool_size initialization."""
        service = StorageService()
        assert service.max_pool_size == 100
        assert service.pools == {}
        assert service.volumes == {}

    def test_init_custom_max_pool_size(self):
        """Test custom max_pool_size initialization."""
        service = StorageService(max_pool_size=50)
        assert service.max_pool_size == 50


class TestCreatePool:
    """Test pool creation functionality."""

    def test_create_pool_success(self):
        """Test successful pool creation."""
        service = StorageService()
        result = service.create_pool("pool-1", 1000)
        assert result is True
        assert "pool-1" in service.pools
        assert service.pools["pool-1"]["size_gb"] == 1000
        assert service.pools["pool-1"]["used_gb"] == 0
        assert service.pools["pool-1"]["status"] == "active"

    def test_create_pool_empty_pool_id(self):
        """Test pool creation with empty pool_id."""
        service = StorageService()
        with pytest.raises(ValueError, match="pool_id cannot be empty"):
            service.create_pool("", 1000)

    def test_create_pool_whitespace_pool_id(self):
        """Test pool creation with whitespace pool_id."""
        service = StorageService()
        with pytest.raises(ValueError, match="pool_id cannot be empty"):
            service.create_pool("   ", 1000)

    def test_create_pool_invalid_size(self):
        """Test pool creation with invalid size."""
        service = StorageService()
        with pytest.raises(ValueError, match="size_gb must be positive"):
            service.create_pool("pool-1", 0)
        with pytest.raises(ValueError, match="size_gb must be positive"):
            service.create_pool("pool-1", -100)

    def test_create_pool_max_limit(self):
        """Test pool creation exceeding max limit."""
        service = StorageService(max_pool_size=2)
        service.create_pool("pool-1", 100)
        service.create_pool("pool-2", 100)
        result = service.create_pool("pool-3", 100)
        assert result is False

    def test_create_multiple_pools(self):
        """Test creating multiple pools."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_pool("pool-2", 2000)
        service.create_pool("pool-3", 3000)
        assert len(service.pools) == 3


class TestDeletePool:
    """Test pool deletion functionality."""

    def test_delete_pool_success(self):
        """Test successful pool deletion."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        result = service.delete_pool("pool-1")
        assert result is True
        assert "pool-1" not in service.pools

    def test_delete_pool_not_found(self):
        """Test deleting non-existent pool."""
        service = StorageService()
        result = service.delete_pool("pool-1")
        assert result is False


class TestCreateVolume:
    """Test volume creation functionality."""

    def test_create_volume_success(self):
        """Test successful volume creation."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        result = service.create_volume("vol-1", "pool-1", 500)
        assert result is True
        assert "vol-1" in service.volumes
        assert service.volumes["vol-1"]["pool_id"] == "pool-1"
        assert service.volumes["vol-1"]["size_gb"] == 500
        assert service.volumes["vol-1"]["status"] == "available"

    def test_create_volume_empty_volume_id(self):
        """Test volume creation with empty volume_id."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        with pytest.raises(ValueError, match="volume_id cannot be empty"):
            service.create_volume("", "pool-1", 500)

    def test_create_volume_invalid_size(self):
        """Test volume creation with invalid size."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        with pytest.raises(ValueError, match="size_gb must be positive"):
            service.create_volume("vol-1", "pool-1", 0)

    def test_create_volume_pool_not_found(self):
        """Test volume creation in non-existent pool."""
        service = StorageService()
        with pytest.raises(KeyError, match="Pool pool-1 not found"):
            service.create_volume("vol-1", "pool-1", 500)

    def test_create_volume_insufficient_space(self):
        """Test volume creation with insufficient pool space."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        result = service.create_volume("vol-1", "pool-1", 800)
        assert result is True
        result = service.create_volume("vol-2", "pool-1", 300)
        assert result is False

    def test_create_volume_updates_pool_usage(self):
        """Test that volume creation updates pool usage."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_volume("vol-1", "pool-1", 300)
        assert service.pools["pool-1"]["used_gb"] == 300
        service.create_volume("vol-2", "pool-1", 200)
        assert service.pools["pool-1"]["used_gb"] == 500


class TestPoolStats:
    """Test pool statistics functionality."""

    def test_get_pool_stats_success(self):
        """Test getting pool statistics."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_volume("vol-1", "pool-1", 300)
        
        stats = service.get_pool_stats("pool-1")
        assert stats["pool_id"] == "pool-1"
        assert stats["total_size_gb"] == 1000
        assert stats["used_gb"] == 300
        assert stats["available_gb"] == 700
        assert stats["utilization_percent"] == 30.0
        assert stats["status"] == "active"

    def test_get_pool_stats_not_found(self):
        """Test getting stats for non-existent pool."""
        service = StorageService()
        stats = service.get_pool_stats("pool-1")
        assert stats == {}

    def test_get_pool_stats_full_pool(self):
        """Test pool stats when completely full."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_volume("vol-1", "pool-1", 1000)
        
        stats = service.get_pool_stats("pool-1")
        assert stats["used_gb"] == 1000
        assert stats["available_gb"] == 0
        assert stats["utilization_percent"] == 100.0


class TestListVolumes:
    """Test volume listing functionality."""

    def test_list_volumes_all(self):
        """Test listing all volumes."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_pool("pool-2", 1000)
        service.create_volume("vol-1", "pool-1", 300)
        service.create_volume("vol-2", "pool-1", 200)
        service.create_volume("vol-3", "pool-2", 400)
        
        volumes = service.list_volumes()
        assert len(volumes) == 3
        assert set(volumes) == {"vol-1", "vol-2", "vol-3"}

    def test_list_volumes_by_pool(self):
        """Test listing volumes filtered by pool."""
        service = StorageService()
        service.create_pool("pool-1", 1000)
        service.create_pool("pool-2", 1000)
        service.create_volume("vol-1", "pool-1", 300)
        service.create_volume("vol-2", "pool-1", 200)
        service.create_volume("vol-3", "pool-2", 400)
        
        volumes = service.list_volumes(pool_id="pool-1")
        assert len(volumes) == 2
        assert set(volumes) == {"vol-1", "vol-2"}

    def test_list_volumes_empty(self):
        """Test listing volumes when none exist."""
        service = StorageService()
        volumes = service.list_volumes()
        assert volumes == []
