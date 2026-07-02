"""Network service for managing HCI network infrastructure."""


class NetworkService:
    """Service to manage network resources and configurations in HCI infrastructure."""

    def __init__(self):
        """Initialize the NetworkService."""
        self.networks = {}
        self.interfaces = {}
        self.vlans = {}

    def create_network(self, network_id: str, cidr: str, vlan_id: int = None) -> bool:
        """
        Create a virtual network.

        Args:
            network_id: Unique identifier for the network.
            cidr: CIDR notation for the network (e.g., '10.0.0.0/24').
            vlan_id: Optional VLAN ID.

        Returns:
            True if network created successfully, False otherwise.

        Raises:
            ValueError: If parameters are invalid.
        """
        if not network_id or network_id.strip() == "":
            raise ValueError("network_id cannot be empty")
        if not cidr or "/" not in cidr:
            raise ValueError("cidr must be in valid format (e.g., 10.0.0.0/24)")

        self.networks[network_id] = {
            "cidr": cidr,
            "vlan_id": vlan_id,
            "status": "active",
            "interfaces": [],
        }
        return True

    def delete_network(self, network_id: str) -> bool:
        """
        Delete a virtual network.

        Args:
            network_id: Unique identifier for the network.

        Returns:
            True if network deleted, False if not found.
        """
        if network_id in self.networks:
            del self.networks[network_id]
            return True
        return False

    def add_interface(
        self, interface_id: str, network_id: str, ip_address: str
    ) -> bool:
        """
        Add a network interface to a network.

        Args:
            interface_id: Unique identifier for the interface.
            network_id: The network to add interface to.
            ip_address: IP address for the interface.

        Returns:
            True if interface added successfully, False otherwise.

        Raises:
            ValueError: If parameters are invalid.
            KeyError: If network_id does not exist.
        """
        if not interface_id or interface_id.strip() == "":
            raise ValueError("interface_id cannot be empty")
        if not ip_address or ip_address.strip() == "":
            raise ValueError("ip_address cannot be empty")
        if network_id not in self.networks:
            raise KeyError(f"Network {network_id} not found")

        self.interfaces[interface_id] = {
            "network_id": network_id,
            "ip_address": ip_address,
            "status": "up",
        }
        self.networks[network_id]["interfaces"].append(interface_id)
        return True

    def remove_interface(self, interface_id: str) -> bool:
        """
        Remove a network interface.

        Args:
            interface_id: Unique identifier for the interface.

        Returns:
            True if interface removed, False if not found.
        """
        if interface_id not in self.interfaces:
            return False

        interface = self.interfaces[interface_id]
        network_id = interface["network_id"]
        self.networks[network_id]["interfaces"].remove(interface_id)
        del self.interfaces[interface_id]
        return True

    def get_network_info(self, network_id: str) -> dict:
        """
        Get information about a network.

        Args:
            network_id: Unique identifier for the network.

        Returns:
            Dictionary with network information or empty dict if not found.
        """
        if network_id not in self.networks:
            return {}
        return self.networks[network_id].copy()

    def list_networks(self, status: str = None) -> list:
        """
        List all networks, optionally filtered by status.

        Args:
            status: Optional status filter.

        Returns:
            List of network IDs.
        """
        if status is None:
            return list(self.networks.keys())
        return [
            net_id
            for net_id, net_info in self.networks.items()
            if net_info["status"] == status
        ]

    def get_interface_info(self, interface_id: str) -> dict:
        """
        Get information about a network interface.

        Args:
            interface_id: Unique identifier for the interface.

        Returns:
            Dictionary with interface information or empty dict if not found.
        """
        if interface_id not in self.interfaces:
            return {}
        return self.interfaces[interface_id].copy()
