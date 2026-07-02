"""Unit tests for NetworkService."""

import pytest
from hci_repo_structure.src.network.network_service import NetworkService


class TestNetworkServiceInitialization:
    """Test NetworkService initialization."""

    def test_init(self):
        """Test NetworkService initialization."""
        service = NetworkService()
        assert service.networks == {}
        assert service.interfaces == {}
        assert service.vlans == {}


class TestCreateNetwork:
    """Test network creation functionality."""

    def test_create_network_success(self):
        """Test successful network creation."""
        service = NetworkService()
        result = service.create_network("net-1", "10.0.0.0/24")
        assert result is True
        assert "net-1" in service.networks
        assert service.networks["net-1"]["cidr"] == "10.0.0.0/24"
        assert service.networks["net-1"]["status"] == "active"
        assert service.networks["net-1"]["interfaces"] == []
        assert service.networks["net-1"]["vlan_id"] is None

    def test_create_network_with_vlan(self):
        """Test network creation with VLAN ID."""
        service = NetworkService()
        result = service.create_network("net-1", "10.0.0.0/24", vlan_id=100)
        assert result is True
        assert service.networks["net-1"]["vlan_id"] == 100

    def test_create_network_empty_network_id(self):
        """Test network creation with empty network_id."""
        service = NetworkService()
        with pytest.raises(ValueError, match="network_id cannot be empty"):
            service.create_network("", "10.0.0.0/24")

    def test_create_network_empty_cidr(self):
        """Test network creation with empty CIDR."""
        service = NetworkService()
        with pytest.raises(ValueError, match="cidr must be in valid format"):
            service.create_network("net-1", "")

    def test_create_network_invalid_cidr_format(self):
        """Test network creation with invalid CIDR format."""
        service = NetworkService()
        with pytest.raises(ValueError, match="cidr must be in valid format"):
            service.create_network("net-1", "10.0.0.0")

    def test_create_multiple_networks(self):
        """Test creating multiple networks."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.create_network("net-2", "10.1.0.0/24", vlan_id=100)
        service.create_network("net-3", "10.2.0.0/24", vlan_id=101)
        assert len(service.networks) == 3


class TestDeleteNetwork:
    """Test network deletion functionality."""

    def test_delete_network_success(self):
        """Test successful network deletion."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        result = service.delete_network("net-1")
        assert result is True
        assert "net-1" not in service.networks

    def test_delete_network_not_found(self):
        """Test deleting non-existent network."""
        service = NetworkService()
        result = service.delete_network("net-1")
        assert result is False


class TestAddInterface:
    """Test interface addition functionality."""

    def test_add_interface_success(self):
        """Test successful interface addition."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        result = service.add_interface("eth0", "net-1", "10.0.0.10")
        assert result is True
        assert "eth0" in service.interfaces
        assert service.interfaces["eth0"]["network_id"] == "net-1"
        assert service.interfaces["eth0"]["ip_address"] == "10.0.0.10"
        assert service.interfaces["eth0"]["status"] == "up"
        assert "eth0" in service.networks["net-1"]["interfaces"]

    def test_add_interface_empty_interface_id(self):
        """Test interface addition with empty interface_id."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        with pytest.raises(ValueError, match="interface_id cannot be empty"):
            service.add_interface("", "net-1", "10.0.0.10")

    def test_add_interface_empty_ip_address(self):
        """Test interface addition with empty IP address."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        with pytest.raises(ValueError, match="ip_address cannot be empty"):
            service.add_interface("eth0", "net-1", "")

    def test_add_interface_network_not_found(self):
        """Test interface addition to non-existent network."""
        service = NetworkService()
        with pytest.raises(KeyError, match="Network net-1 not found"):
            service.add_interface("eth0", "net-1", "10.0.0.10")

    def test_add_multiple_interfaces_to_network(self):
        """Test adding multiple interfaces to a network."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.add_interface("eth0", "net-1", "10.0.0.10")
        service.add_interface("eth1", "net-1", "10.0.0.11")
        service.add_interface("eth2", "net-1", "10.0.0.12")
        
        assert len(service.networks["net-1"]["interfaces"]) == 3
        assert set(service.networks["net-1"]["interfaces"]) == {"eth0", "eth1", "eth2"}


class TestRemoveInterface:
    """Test interface removal functionality."""

    def test_remove_interface_success(self):
        """Test successful interface removal."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.add_interface("eth0", "net-1", "10.0.0.10")
        result = service.remove_interface("eth0")
        assert result is True
        assert "eth0" not in service.interfaces
        assert "eth0" not in service.networks["net-1"]["interfaces"]

    def test_remove_interface_not_found(self):
        """Test removing non-existent interface."""
        service = NetworkService()
        result = service.remove_interface("eth0")
        assert result is False

    def test_remove_interface_updates_network(self):
        """Test that interface removal updates network interfaces list."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.add_interface("eth0", "net-1", "10.0.0.10")
        service.add_interface("eth1", "net-1", "10.0.0.11")
        
        assert len(service.networks["net-1"]["interfaces"]) == 2
        service.remove_interface("eth0")
        assert len(service.networks["net-1"]["interfaces"]) == 1
        assert service.networks["net-1"]["interfaces"] == ["eth1"]


class TestGetNetworkInfo:
    """Test network info retrieval functionality."""

    def test_get_network_info_success(self):
        """Test successful network info retrieval."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24", vlan_id=100)
        service.add_interface("eth0", "net-1", "10.0.0.10")
        
        info = service.get_network_info("net-1")
        assert info["cidr"] == "10.0.0.0/24"
        assert info["vlan_id"] == 100
        assert info["status"] == "active"
        assert "eth0" in info["interfaces"]

    def test_get_network_info_not_found(self):
        """Test getting info for non-existent network."""
        service = NetworkService()
        info = service.get_network_info("net-1")
        assert info == {}

    def test_get_network_info_returns_copy(self):
        """Test that get_network_info returns a copy."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        info = service.get_network_info("net-1")
        info["status"] = "modified"
        assert service.networks["net-1"]["status"] == "active"


class TestListNetworks:
    """Test network listing functionality."""

    def test_list_networks_all(self):
        """Test listing all networks."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.create_network("net-2", "10.1.0.0/24")
        service.create_network("net-3", "10.2.0.0/24")
        
        networks = service.list_networks()
        assert len(networks) == 3
        assert set(networks) == {"net-1", "net-2", "net-3"}

    def test_list_networks_by_status(self):
        """Test listing networks filtered by status."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.create_network("net-2", "10.1.0.0/24")
        service.create_network("net-3", "10.2.0.0/24")
        
        networks = service.list_networks(status="active")
        assert len(networks) == 3
        assert set(networks) == {"net-1", "net-2", "net-3"}

    def test_list_networks_empty(self):
        """Test listing networks when none exist."""
        service = NetworkService()
        networks = service.list_networks()
        assert networks == []


class TestGetInterfaceInfo:
    """Test interface info retrieval functionality."""

    def test_get_interface_info_success(self):
        """Test successful interface info retrieval."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.add_interface("eth0", "net-1", "10.0.0.10")
        
        info = service.get_interface_info("eth0")
        assert info["network_id"] == "net-1"
        assert info["ip_address"] == "10.0.0.10"
        assert info["status"] == "up"

    def test_get_interface_info_not_found(self):
        """Test getting info for non-existent interface."""
        service = NetworkService()
        info = service.get_interface_info("eth0")
        assert info == {}

    def test_get_interface_info_returns_copy(self):
        """Test that get_interface_info returns a copy."""
        service = NetworkService()
        service.create_network("net-1", "10.0.0.0/24")
        service.add_interface("eth0", "net-1", "10.0.0.10")
        
        info = service.get_interface_info("eth0")
        info["status"] = "modified"
        assert service.interfaces["eth0"]["status"] == "up"
