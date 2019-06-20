from graphutil import Graph


def test_arcs():
    g = Graph()

    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")

    g.add_edge("A", "B", "edge_data")
    g.add_edge("A", "C", "edge_data")
    g.add_edge("A", "D", "edge_data")
    g.add_edge("B", "D", "edge_data")
    g.add_edge("C", "D", "edge_data")

    # inarcs
    if len(g.in_arcs("A")) or len(g.in_arcs_data("A")):
        assert False

    if len(g.in_arcs("B")) != 1 or len(g.in_arcs_data("B")) != 1:
        assert False

    if len(g.in_arcs("C")) != 1 or len(g.in_arcs_data("C")) != 1:
        assert False

    if len(g.in_arcs("D")) != 3 or len(g.in_arcs_data("D")) != 3:
        assert False

    # outarcs
    if len(g.out_arcs("D")) or len(g.out_arcs_data("D")):
        assert False

    if len(g.out_arcs("B")) != 1 or len(g.out_arcs_data("B")) != 1:
        assert False

    if len(g.out_arcs("C")) != 1 or len(g.out_arcs_data("C")) != 1:
        assert False

    if len(g.out_arcs("A")) != 3 or len(g.out_arcs_data("A")) != 3:
        assert False

    assert True


def test_write():
    g = Graph()

    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")

    g.add_edge("A", "B", "edge_data")
    g.add_edge("A", "C", "edge_data")
    g.add_edge("A", "D", "edge_data")
    g.add_edge("B", "D", "edge_data")
    g.add_edge("C", "D", "edge_data")
    g.write('test_graph')


def test_connected_components():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")

    g.add_edge("A", "B", "edge_data")
    g.add_edge("A", "C", "edge_data")
    g.add_edge("A", "D", "edge_data")
    g.add_edge("B", "D", "edge_data")
    g.add_edge("C", "D", "edge_data")

    g.add_node("E")
    g.add_node("F")
    g.add_node("G")
    g.add_node("W")

    g.add_edge("E", "F", "edge_data")
    g.add_edge("E", "G", "edge_data")
    g.add_edge("E", "W", "edge_data")
    g.add_edge("F", "W", "edge_data")
    g.add_edge("G", "W", "edge_data")

    groups = g.connected_components()
    if not len(groups) == 2:
        assert False
    for group in groups:
        if "A" in group:
            if not set(['B', 'C', 'D']).issubset(group):
                assert False
        elif "E" in group:
            if not set(['F', 'G', 'W']).issubset(group):
                assert False
        if len(group) != 4:
            assert False
    assert True


if __name__ == "__main__":
    test_arcs()
    test_write()
    test_connected_components()
