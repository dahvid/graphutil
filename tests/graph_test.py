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

def test_bfs():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")
    g.add_node("F")

    g.add_edge("A", "B", "edge_data")
    g.add_edge("B", "C", "edge_data")
    g.add_edge("C", "D", "edge_data")
    g.add_edge("B", "D", "edge_data")
    bfs = g.bfs("A")
    # print(bfs)
    assert bfs == ["A","B","C","D"]

def test_bfs_full():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")
    g.add_node("F")

    g.add_edge("A", "B", "edge_data")
    g.add_edge("A", "D", "edge_data")
    g.add_edge("B", "C", "edge_data")
    g.add_edge("B", "D", "edge_data")
    bfs = g.bfs_full()
    assert len(bfs)
    assert bfs == ['A', 'E', 'F', 'B', 'D', 'C']

def test_substitute():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")

    g.add_edge("A", "B", "a-b data")
    g.add_edge("B", "C", "b-c data")

    s = Graph()
    s.add_node("B")
    s.add_node("D")
    s.add_edge("B","D","b-d data")

    g.substitute("B",s)
    assert len(g.node_list()) == 4
    assert set(g.node_list()) == {'A','B','C','D'}

def test_multi():
    g = Graph()

    g.add_node("A")
    g.add_node("B")
    g.add_node("C")

    g.add_edge("A", "B", "a-b data")
    g.add_edge("B", "C", "b-c data")
    g.add_edge("A", "B", "other data")
    assert g.number_of_multi_edges("A","B") == 2

def test_subgraphs():
    g = Graph()

    g.add_node("A",'a')
    g.add_node("B",'b')
    g.add_node("C",'c')

    g.add_edge("A", "B", "a-b data")
    g.add_edge("B", "C", "b-c data")

    g.add_subgraph('test',['B','C'])

    sg,_,_ = g.induce_subgraph('test')
    assert(sg.node_data('B') == 'b')
    assert(sg.node_data('C') == 'c')
    edges = sg.get_edges('B','C')
    assert(len(edges) == 1)
    assert(sg.get_edge_attributes(edges[0]) == 'b-c data')
    sg.set_node_data("B",'new data')
    assert(g.node_data('B') == 'b' and sg.node_data('B') == 'new data')
    # print(f'subgraph edge = {sg.edge_list()}')




if __name__ == "__main__":
    # test_arcs()
    # test_write()
    # test_connected_components()
    # test_bfs()
    # test_bfs_full()
    # test_substitute()
    # test_multi()
    test_subgraphs()
