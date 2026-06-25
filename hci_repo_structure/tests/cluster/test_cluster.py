# tests for cluster mapped to ClusterService API

from hci_repo_structure.src.cluster.cluster_service import ClusterService


def test_cluster_add_remove_get_size():
    svc = ClusterService()
    # initially empty
    assert svc.size() == 0
    assert svc.get_nodes() == []

    # add node1
    assert svc.add_node("node1") is True
    assert svc.size() == 1
    # adding duplicate returns False and does not increase size
    assert svc.add_node("node1") is False
    assert svc.get_nodes() == ["node1"]

    # add another node
    assert svc.add_node("node2") is True
    assert svc.get_nodes() == ["node1", "node2"]
    assert svc.size() == 2

    # removing a non-existent node returns False
    assert svc.remove_node("node3") is False

    # remove existing node
    assert svc.remove_node("node1") is True
    assert svc.get_nodes() == ["node2"]
    assert svc.size() == 1


def test_cluster_init_with_nodes_and_ordering():
    svc = ClusterService(nodes=["a", "b", "a"])  # duplicate 'a' should be deduped
    # insertion order preserved, duplicates removed
    assert svc.get_nodes() == ["a", "b"]
    assert svc.size() == 2
