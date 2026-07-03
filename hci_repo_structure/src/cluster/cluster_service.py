# cluster service - Editing it for new PR

class ClusterService:
    """A minimal cluster service used by tests.

    It maintains a set of node identifiers and provides simple operations:
    - add_node(node): adds a node (no-op if already present), returns True if added
    - remove_node(node): removes a node, returns True if removed
    - get_nodes(): returns a tuple of nodes in insertion order
    - size(): returns number of nodes

    The implementation uses an internal set to keep nodes unique while preserving
    insertion order for get_nodes using a list for deterministic order.
    """

    def __init__(self, nodes=None):
        self._nodes_set = set()
        self._nodes_order = []
        if nodes:
            for n in nodes:
                self.add_node(n)

    def add_node(self, node):
        """Add a node to the cluster.

        Returns True if the node was added, False if it was already present.
        """
        if node in self._nodes_set:
            return False
        self._nodes_set.add(node)
        self._nodes_order.append(node)
        return True

    def remove_node(self, node):
        """Remove a node from the cluster.

        Returns True if the node was removed, False if it was not present.
        """
        if node not in self._nodes_set:
            return False
        self._nodes_set.remove(node)
        self._nodes_order.remove(node)
        return True

    def get_nodes(self):
        """Return the tuple of nodes in insertion order."""
        return tuple(self._nodes_order)

    def size(self):
        """Return the number of nodes in the cluster."""
        return len(self._nodes_order)
