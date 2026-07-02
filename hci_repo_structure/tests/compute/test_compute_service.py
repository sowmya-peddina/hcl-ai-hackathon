"""Unit tests for ComputeService."""

import pytest
from hci_repo_structure.src.compute.compute_service import ComputeService


class TestComputeServiceInitialization:
    """Test ComputeService initialization."""

    def test_init_default_max_vms(self):
        """Test default max_vms initialization."""
        service = ComputeService()
        assert service.max_vms == 1000
        assert service.vms == {}
        assert service.resources["total_cpu"] == 0
        assert service.resources["total_memory_gb"] == 0

    def test_init_custom_max_vms(self):
        """Test custom max_vms initialization."""
        service = ComputeService(max_vms=500)
        assert service.max_vms == 500


class TestRegisterHost:
    """Test host registration functionality."""

    def test_register_host_success(self):
        """Test successful host registration."""
        service = ComputeService()
        result = service.register_host("host-1", 16, 64)
        assert result is True
        assert service.resources["total_cpu"] == 16
        assert service.resources["total_memory_gb"] == 64

    def test_register_host_empty_host_id(self):
        """Test host registration with empty host_id."""
        service = ComputeService()
        with pytest.raises(ValueError, match="host_id cannot be empty"):
            service.register_host("", 16, 64)

    def test_register_host_invalid_cpu_cores(self):
        """Test host registration with invalid CPU cores."""
        service = ComputeService()
        with pytest.raises(ValueError, match="cpu_cores must be positive"):
            service.register_host("host-1", 0, 64)
        with pytest.raises(ValueError, match="cpu_cores must be positive"):
            service.register_host("host-1", -8, 64)

    def test_register_host_invalid_memory(self):
        """Test host registration with invalid memory."""
        service = ComputeService()
        with pytest.raises(ValueError, match="memory_gb must be positive"):
            service.register_host("host-1", 16, 0)
        with pytest.raises(ValueError, match="memory_gb must be positive"):
            service.register_host("host-1", 16, -32)

    def test_register_multiple_hosts(self):
        """Test registering multiple hosts."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.register_host("host-2", 8, 32)
        service.register_host("host-3", 32, 128)
        
        assert service.resources["total_cpu"] == 56
        assert service.resources["total_memory_gb"] == 224


class TestCreateVM:
    """Test VM creation functionality."""

    def test_create_vm_success(self):
        """Test successful VM creation."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        result = service.create_vm("vm-1", "host-1", 4, 8)
        assert result is True
        assert "vm-1" in service.vms
        assert service.vms["vm-1"]["host_id"] == "host-1"
        assert service.vms["vm-1"]["cpu_cores"] == 4
        assert service.vms["vm-1"]["memory_gb"] == 8
        assert service.vms["vm-1"]["status"] == "running"

    def test_create_vm_empty_vm_id(self):
        """Test VM creation with empty vm_id."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        with pytest.raises(ValueError, match="vm_id cannot be empty"):
            service.create_vm("", "host-1", 4, 8)

    def test_create_vm_invalid_cpu_cores(self):
        """Test VM creation with invalid CPU cores."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        with pytest.raises(ValueError, match="cpu_cores must be positive"):
            service.create_vm("vm-1", "host-1", 0, 8)

    def test_create_vm_invalid_memory(self):
        """Test VM creation with invalid memory."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        with pytest.raises(ValueError, match="memory_gb must be positive"):
            service.create_vm("vm-1", "host-1", 4, 0)

    def test_create_vm_max_limit(self):
        """Test VM creation exceeding max limit."""
        service = ComputeService(max_vms=2)
        service.register_host("host-1", 100, 256)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        result = service.create_vm("vm-3", "host-1", 4, 8)
        assert result is False

    def test_create_multiple_vms(self):
        """Test creating multiple VMs."""
        service = ComputeService()
        service.register_host("host-1", 32, 128)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        service.create_vm("vm-3", "host-1", 8, 16)
        assert len(service.vms) == 3


class TestPowerOffVM:
    """Test VM power off functionality."""

    def test_power_off_vm_success(self):
        """Test successful VM power off."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.create_vm("vm-1", "host-1", 4, 8)
        result = service.power_off_vm("vm-1")
        assert result is True
        assert service.vms["vm-1"]["status"] == "stopped"

    def test_power_off_vm_not_found(self):
        """Test powering off non-existent VM."""
        service = ComputeService()
        result = service.power_off_vm("vm-1")
        assert result is False


class TestDeleteVM:
    """Test VM deletion functionality."""

    def test_delete_vm_success(self):
        """Test successful VM deletion."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.create_vm("vm-1", "host-1", 4, 8)
        result = service.delete_vm("vm-1")
        assert result is True
        assert "vm-1" not in service.vms

    def test_delete_vm_not_found(self):
        """Test deleting non-existent VM."""
        service = ComputeService()
        result = service.delete_vm("vm-1")
        assert result is False


class TestGetVMInfo:
    """Test VM info retrieval functionality."""

    def test_get_vm_info_success(self):
        """Test successful VM info retrieval."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.create_vm("vm-1", "host-1", 4, 8)
        info = service.get_vm_info("vm-1")
        assert info["host_id"] == "host-1"
        assert info["cpu_cores"] == 4
        assert info["memory_gb"] == 8
        assert info["status"] == "running"

    def test_get_vm_info_not_found(self):
        """Test getting info for non-existent VM."""
        service = ComputeService()
        info = service.get_vm_info("vm-1")
        assert info == {}

    def test_get_vm_info_returns_copy(self):
        """Test that get_vm_info returns a copy, not reference."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.create_vm("vm-1", "host-1", 4, 8)
        info = service.get_vm_info("vm-1")
        info["status"] = "modified"
        assert service.vms["vm-1"]["status"] == "running"


class TestListVMs:
    """Test VM listing functionality."""

    def test_list_vms_all(self):
        """Test listing all VMs."""
        service = ComputeService()
        service.register_host("host-1", 100, 256)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        service.create_vm("vm-3", "host-1", 4, 8)
        
        vms = service.list_vms()
        assert len(vms) == 3
        assert set(vms) == {"vm-1", "vm-2", "vm-3"}

    def test_list_vms_by_host(self):
        """Test listing VMs filtered by host."""
        service = ComputeService()
        service.register_host("host-1", 100, 256)
        service.register_host("host-2", 100, 256)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        service.create_vm("vm-3", "host-2", 4, 8)
        
        vms = service.list_vms(host_id="host-1")
        assert len(vms) == 2
        assert set(vms) == {"vm-1", "vm-2"}

    def test_list_vms_by_status(self):
        """Test listing VMs filtered by status."""
        service = ComputeService()
        service.register_host("host-1", 100, 256)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        service.create_vm("vm-3", "host-1", 4, 8)
        service.power_off_vm("vm-2")
        
        running_vms = service.list_vms(status="running")
        assert len(running_vms) == 2
        assert set(running_vms) == {"vm-1", "vm-3"}
        
        stopped_vms = service.list_vms(status="stopped")
        assert len(stopped_vms) == 1
        assert stopped_vms == ["vm-2"]

    def test_list_vms_by_host_and_status(self):
        """Test listing VMs filtered by both host and status."""
        service = ComputeService()
        service.register_host("host-1", 100, 256)
        service.register_host("host-2", 100, 256)
        service.create_vm("vm-1", "host-1", 4, 8)
        service.create_vm("vm-2", "host-1", 4, 8)
        service.create_vm("vm-3", "host-2", 4, 8)
        service.power_off_vm("vm-2")
        service.power_off_vm("vm-3")
        
        vms = service.list_vms(host_id="host-1", status="running")
        assert vms == ["vm-1"]

    def test_list_vms_empty(self):
        """Test listing VMs when none exist."""
        service = ComputeService()
        vms = service.list_vms()
        assert vms == []


class TestGetTotalResources:
    """Test total resources retrieval functionality."""

    def test_get_total_resources(self):
        """Test getting total resources."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        service.register_host("host-2", 8, 32)
        
        resources = service.get_total_resources()
        assert resources["total_cpu"] == 24
        assert resources["total_memory_gb"] == 96

    def test_get_total_resources_returns_copy(self):
        """Test that get_total_resources returns a copy."""
        service = ComputeService()
        service.register_host("host-1", 16, 64)
        resources = service.get_total_resources()
        resources["total_cpu"] = 999
        assert service.resources["total_cpu"] == 16
