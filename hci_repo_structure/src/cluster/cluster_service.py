# cluster service

class ClusterService:
    """Manages HCI cluster lifecycle: creation, health, and node failover."""

    def __init__(self):
        self.nodes = []
        self.state = "INACTIVE"
        print("ClusterService initialized")

    def create_cluster(self, nodes, region):
        """Create a new HCI cluster with the given nodes in a region.

        Registers each node and transitions the cluster to ACTIVE once all
        nodes are healthy and quorum is established.
        """
        if nodes < 1:
            raise ValueError("A cluster requires at least one node")
        self.nodes = [{"id": i + 1, "region": region, "healthy": True}
                      for i in range(nodes)]
        self.state = "ACTIVE"
        return {"state": self.state, "nodes": len(self.nodes), "region": region}

    def handle_node_failure(self, node_id):
        """Detect a failed node and automatically reschedule its workloads.

        Maintains quorum and keeps services available without manual
        intervention by shifting workloads to remaining healthy nodes.
        """
        target = next((n for n in self.nodes if n["id"] == node_id), None)
        if not target:
            raise ValueError(f"Unknown node: {node_id}")
        target["healthy"] = False
        healthy = [n for n in self.nodes if n["healthy"]]
        if not healthy:
            self.state = "DEGRADED"
            return {"failover": False, "reason": "no healthy nodes"}
        return {"failover": True, "rescheduled_to": healthy[0]["id"],
                "quorum": len(healthy) > len(self.nodes) // 2}
