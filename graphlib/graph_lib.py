## @package graph_lib
#  Copyright (c) General Electric Company, 2017. All rights reserved.
#


#--Version 1.0.0
#--Nathan Denny, May 27, 1999
#--Version 1.1.0
#--David Minor, Sept 1, 2008
#--Version 1.2.0
#--David Minor, April 30, 2009
#--Version 1.3.0
#--David Minor, June 11, 2009
#--Version 1.4.0
#--David Minor, Anatoly Ganapolski, September 27, 2012
#--Version 1.5.0
#--David Minor  January 14, 2016
#--Version 1.6.0
#--David Minor April 9, 2018

has_graphviz = True
try:
	import pygraphviz as pgv
except:
	has_graphviz = False

import copy
import time
import pprint
import logging
import traceback,sys
from collections import defaultdict


#
# Exceptions
#
class Graph_duplicate_node(Exception):
	pass

class Graph_topological_error(Exception):
	pass

class Graph_dandling_edge(Exception):
	pass


"""

	Tarjan's algorithm and topological sorting implementation in Python

	by Paul Harrison

	Public domain, do with it as you will

"""

def strongly_connected_components(graph):
	"""
	Tarjan's Algorithm (named for its discoverer, Robert Tarjan) is a graph theory algorithm
	for finding the strongly connected components of a graph.

	Based on: http://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
	"""

	index_counter = [0]
	stack = []
	lowlinks = {}
	index = {}
	result = []

	def strongconnect(node):
		# set the depth index for this node to the smallest unused index
		index[node] = index_counter[0]
		lowlinks[node] = index_counter[0]
		index_counter[0] += 1
		stack.append(node)

		# Consider successors of `node`
		try:
			successors = graph[node]
		except:
			successors = []
		for successor in successors:
			if successor not in lowlinks:
				# Successor has not yet been visited; recurse on it
				strongconnect(successor)
				lowlinks[node] = min(lowlinks[node],lowlinks[successor])
			elif successor in stack:
				# the successor is in the stack and hence in the current strongly connected component (SCC)
				lowlinks[node] = min(lowlinks[node],index[successor])

		# If `node` is a root node, pop the stack and generate an SCC
		if lowlinks[node] == index[node]:
			connected_component = []

			while True:
				successor = stack.pop()
				connected_component.append(successor)
				if successor == node: break
			component = tuple(connected_component)
			# storing the result
			result.append(component)

	for node in graph:
		if node not in lowlinks:
			strongconnect(node)

	return result


def topological_sort(graph):
	count = { }
	for node in graph:
		count[node] = 0
	for node in graph:
		for successor in graph[node]:
			count[successor] += 1

	ready = [ node for node in graph if count[node] == 0 ]

	result = [ ]
	while ready:
		node = ready.pop(-1)
		result.append(node)

		for successor in graph[node]:
			count[successor] -= 1
			if count[successor] == 0:
				ready.append(successor)

	return result


def robust_topological_sort(graph):
	""" First identify strongly connected components,
		then perform a topological sort on these components. """

	components = strongly_connected_components(graph)

	node_component = { }
	for component in components:
		for node in component:
			node_component[node] = component

	component_graph = { }
	for component in components:
		component_graph[component] = [ ]

	for node in graph:
		node_c = node_component[node]
		for successor in graph[node]:
			successor_c = node_component[successor]
			if node_c != successor_c:
				component_graph[node_c].append(successor_c)

	return topological_sort(component_graph)



class GraphQueue:
	def __init__(self):
		self.q=[]

	def empty(self):
		if(len(self.q)>0):
			return 0
		else:
			return 1

	def count(self):
		return len(self.q)

	def add(self, item):
		self.q.append(item)

	def remove(self):
		item=self.q[0]
		self.q=self.q[1:]
		return item

class GraphStack:
	def __init__(self):
		self.s=[]

	def empty(self):
		if(len(self.s)>0):
			return 0
		else:
			return 1

	def count(self):
		return len(self.s)

	def push(self, item):
		self.s.append(item)

	def pop(self):
		return self.s.pop()   # extract last element & return it.

	def top(self):
		return self.s[-1:][0] # return last element

	def clone(self):
		NewStack = GraphStack()
		NewStack.s = list(self.s)
		return NewStack

# User doesn't need inner stack representation.
#    def stack(self):
#        return self.s

class Graph:

	def __init__(self):
		self.next_edge_id=0
		self.nodes={}
		self.edges={}
		self.hidden_edges={}
		self.hidden_nodes={}
		self.adjacency_list={}
		self.topo_sort=[]
		self.topo_loc = {}
		self.graph_attributes = {}
		self.closure={}
		self.dfs_list={}

	def clear(self):
		self.__init__()

	def set(self, name, value):
		self.graph_attributes[name] = value

	def get(self, name):
		return self.graph_attributes[name]


	def attr_dict(self):
		return self.graph_attributes


	#--Transforms the graph into it's transative reduction
	#--as the original, can be used to eliminate redundent dependencies
	#--transative reduction is the minumum graph with the same transative closure as
	#--the original
	#--currently only works with DAG's
	def transitive_reduction(self):
		#print 'reducing graph'
		#t0 = time.time()
		self.transitive_closure()
		#print 'reducing over ',len(self.edge_list()),'edges', len(self.node_list()), 'nodes'

		for n in self.node_list():
			inputs = self.in_arcs(n)
			if len(inputs) > 1:
				for e in inputs:
					if self.head(e) == self.tail(e):
						continue
					paths = self.paths(self.head(e),n)
					if paths > 1:
						self.delete_edge(e)
		#print 'done reducing', len(self.edge_list()), 'edges in', time.time() - t0, 'seconds'

	#idea is to write a .gml file for reading with a graph editor
	#and executable python file for further manipulation and reading
	#with our run-time
	#!!!there is non-generic stuff here, get rid of it
	def write(self, name):


		#no edges is allowed (one node)
		#but no nodes is a no no
		if len(self.node_list()) == 0:
			raise BaseException('ERROR GRAPH EMPTY NO NODES')

		#this will write the graph as a graph_viz .dot file
		if has_graphviz:
			#self.transitive_reduction()
			write_graph = pgv.AGraph(directed=True)
			for o in self.node_list():
				write_graph.add_node(o)
			for e in self.edge_list():
				write_graph.add_edge(self.head(e), self.tail(e))
			write_graph.write(name + '.dot')

		#this will write the graph as a python compilable file
		# Graph = {
		# 	'nodes' : { node id : (node data) }
		# 	'edges' : { (src node id, dest node id) : (edge data) }
		#   'attributes' : { attribute : value }
		# }

		#pure python representation
		py_graph = { 'nodes' : self.node_dict(), 'edges' : self.edge_dict(), 'attributes' : self.attr_dict() }
		f = open(name+'_graph.py', 'w')
		pretty_printer = pprint.PrettyPrinter(indent=4)
		nice_str = pretty_printer.pformat(py_graph)
		f.write('GraphDict = ' + nice_str)


	#pure Warshals algorithm, but adapted to existing data structures
	def transitive_closure(self):
		#print('computing closure')
		t0 = time.time()
		new_edges = set()
		edge_list = []
		for e in self.edges:
			head = self.head(e)
			tail = self.tail(e)
			if e in self.edges and head != tail:
				edge_list += [(head,tail)]
		edge_set = frozenset(edge_list)
		for edge in edge_set:
			for i in self.nodes:
				if not i in edge:
					if (edge[1],i) in edge_set:
						new_edges.add((edge[0],i))

		self.closure = copy.deepcopy(self.out_adjacency_list())
		for new_edge in new_edges:
			self.closure[new_edge[0]] += [new_edge[1]]
		#print('done closure', time.time() - t0, "seconds")


	#--Performs a copy of the graph, G, into self.
	#--hidden edges and hidden nodes are not copied.
	#--node_id's remain consistent across self and G,
	#--however edge_id's do not remain consistent.
	#--Need to implement copy operator on node_data
	#--and edge data.
	def copy(self, G):
		#--Blank self.
		self.nodes={}
		self.edges={}
		self.hidden_edges={}
		self.hidden_nodes={}
		self.next_edge_id=0
		#--Copy nodes.
		G_node_list=G.node_list()
		for G_node in G_node_list:
			self.add_node(G_node,G.node_data(G_node))
		#--Copy edges.
		for G_node in G_node_list:
			out_edges=G.out_arcs(G_node)
		for edge in out_edges:
			tail_id=G.tail(edge)
			self.add_edge(G_node, tail_id, G.edge_data(edge))
		self.adjacency_list = G.adjacency_list

	#--Creates a new node with id node_id.  Arbitrary data can be attached
	#--to the node viea the node_data parameter.
	def add_node(self, node_id, node_data=None):
		if not node_id in [self.nodes, self.hidden_nodes]:
			self.nodes[node_id]=([],[],node_data)
			return self.nodes[node_id][2]
		else:
			#print "WARNING: Duplicate node id's.  Latest node id was ignored."
			raise (Graph_duplicate_node, node_id)

	#--Deletes the node and all in and out arcs.
	def delete_node(self, node_id):
		#--Remove fanin connections.
		in_edges=self.in_arcs(node_id)
		for edge in in_edges:
			self.delete_edge(edge)
		#--Remove fanout connections.
		out_edges=self.out_arcs(node_id)
		for edge in out_edges:
			self.delete_edge(edge)
		#--Delete node.
		del self.nodes[node_id]

	#--Delets the edge.
	def delete_edge(self, edge_id):
		head_id= self.head(edge_id)
		tail_id= self.tail(edge_id)
		head_data= self.nodes[head_id]
		tail_data= self.nodes[tail_id]
		head_data[1].remove(edge_id)
		tail_data[0].remove(edge_id)
		del self.edges[edge_id]

	#--Adds an edge (head_id, tail_id).
	#--Arbitrary data can be attached to the edge via edge_data
	def add_edge(self, head_id, tail_id, edge_data=None):
		if (head_id not in self.nodes.keys()) or (tail_id not in self.nodes.keys()):
			nodes_ids_str = '"' + str(head_id) + '" & "' + str(tail_id) + '"'
			raise Graph_dandling_edge("you can't add edge connecting " + nodes_ids_str + " before adding nodes: " + nodes_ids_str)

		edge_id=self.next_edge_id
		self.next_edge_id=self.next_edge_id+1
		self.edges[edge_id]=(head_id, tail_id, edge_data)
		self.nodes[head_id][1].append(edge_id)
		self.nodes[tail_id][0].append(edge_id)
		#mapped_head_data=map(None, self.nodes[head_id])
		#mapped_head_data[1].append(edge_id)
		#mapped_tail_data=map(None, self.nodes[tail_id])
		#mapped_tail_data[0].append(edge_id)
		return edge_id

	#--Removes the edge from the normal graph, but does not delete
	#--its information.  The edge is held in a separate structure
	#--and can be unhidden at some later time.
	def hide_edge(self, edge_id):
		self.hidden_edges[edge_id]=self.edges[edge_id]
		ed=map(None, self.edges[edge_id])
		head_id=ed[0]
		tail_id=ed[1]
		hd=map(None, self.nodes[head_id])
		td=map(None, self.nodes[tail_id])
		hd[1].remove(edge_id)
		td[0].remove(edge_id)
		del self.edges[edge_id]

	#--Similar to above.
	#--Stores a tuple of the node data, and the edges that are incident to and from
	#--the node.  It also hides the incident edges.
	def hide_node(self, node_id):
		degree_list=self.arc_list(node_id)
		self.hidden_nodes[node_id]=(self.nodes[node_id],degree_list)
		for edge in degree_list:
			self.hide_edge(edge)
		del self.nodes[node_id]

	#--Restores a previously hidden edge back into the graph.
	def restore_edge(self, edge_id):
		self.edges[edge_id]=self.hidden_edges[edge_id]
		ed=map(None,self.hidden_edges[edge_id])
		head_id=ed[0]
		tail_id=ed[1]
		hd=map(None,self.nodes[head_id])
		td=map(None,self.nodes[tail_id])
		hd[1].append(edge_id)
		td[0].append(edge_id)
		del self.hidden_edges[edge_id]

	#--Restores all hidden edges.
	def restore_all_edges(self):
		hidden_edge_list=self.hidden_edges.keys()
		for edge in hidden_edge_list:
			self.restore_edge(edge)

	#--Restores a previously hidden node back into the graph
	#--and restores all of the hidden incident edges, too.
	def restore_node(self, node_id):
		hidden_node_data=map(None,self.hidden_nodes[node_id])
		self.nodes[node_id]=hidden_node_data[0]
		degree_list=hidden_node_data[1]
		for edge in degree_list:
			self.restore_edge(edge)
		del self.hidden_nodes[node_id]

	#--Restores all hidden nodes.
	def restore_all_nodes(self):
		for n in map(None, self.hidden_nodes):
			self.restore_node(n)
		self.hidden_nodes = []

		"""
		hidden_node_list=self.nodes.keys()
		for node in hidden_node_list:
			self.nodes[node]=self.hidden_nodes[node]
			del self.hidden_nodes[node]

		"""
	#--Returns 1 if the node_id is in the graph and 0 otherwise.
	def has_node(self, node_id):
		if self.nodes.has_key(node_id):
			return 1
		else:
			return 0

	#--Returns 1 if the edge is in the graph and 0 otherwise.
	def has_edge(self, head_id, tail_id):
		try:
			edge = self.edge(head_id, tail_id)
			return 1
		except :
			return 0

	#--Returns the edge that connects (head_id,tail_id)
	def edge(self, head_id, tail_id):
		out_edges=self.out_arcs(head_id)
		for edge in out_edges:
			if self.tail(edge)==tail_id:
					return edge
		raise (Graph_no_edge, (head_id, tail_id))
		#print "WARNING: No edge to return."

	def number_of_nodes(self):
		return len(self.nodes.keys())

	def number_of_edges(self):
		return len(self.edges.keys())

	def node_dict(self):
		return dict([(x, self.node_data(x)) for x in self.node_list()])

	#--Return a list of the node id's of all visible nodes in the graph.
	def node_list(self):
		return self.nodes.keys()


	#--Return a list of leaf nodes
	def leaves(self):
		leaf_list = []
		for node in self.node_list():
			if self.out_arcs(node) == []:
				leaf_list += [node]
		return leaf_list


	#--Return a list of the node data objects of all visible nodes in the graph.
	def node_data_list(self):
		return [self.node_data(id) for id in self.node_list()]

	#--Similar to above.
	def edge_list(self):
		el=self.edges.keys()
		return el

	#--Similar to above.
	def edge_data_list(self):
		el=self.edges.keys()
		return [self.edge_data(id) for id in el]

	def edge_dict(self):
		return { (self.head(id), self.tail(id)) : self.edge_data(id) for id in self.edges.keys() }


	def number_of_hidden_edges(self):
		return len(self.hidden_edges.keys())

	def number_of_hidden_nodes(self):
		return len(self.hidden_nodes.keys())

	def hidden_node_list(self):
		hnl=self.hidden_nodes.keys()
		return hnl[:]

	def hidden_edge_list(self):
		hel=self.hidden_edges.keys()
		return hel[:]

	#--Returns a reference to the data attached to a node.
	def node_data(self, node_id):
		return self.nodes[node_id][2]

	#--Allows to change data attached to a node
	#--preserves the built-in data and sets only user data
	def set_node_data(self,node_id,data):
		self.nodes[node_id]=(self.nodes[node_id][0],self.nodes[node_id][1],data)

	#--Returns a reference to the data attached to an edge.
	def edge_data(self, edge_id):
		return self.edges[edge_id]

	#--Returns a reference to the head of the edge.  (A reference to the head id)
	def head(self, edge):
		return self.edges[edge][0]

	#--Returns a reference to the head data of the edge.  (A reference to the head data)
	def head_data(self, edge):
		return self.edges[edge]

	#--Similar to above.
	def tail(self, edge):
		return self.edges[edge][1]

	#--Similar to above.
	def tail_data(self, edge):
		mapped_data=map(None, self.edges[edge])
		return self.node_data(mapped_data[1])

	#--Returns a copy of the list of edges of the node's out arcs.
	def out_arcs(self, node_id):
		return self.nodes[node_id][1]

	#--Returns a copy of the list of edge data of the node's out arcs.
	def out_arcs_data(self, node_id):
		mapped_data=map(None, self.nodes[node_id])
		return [self.edge_data(edge_id) for edge_id in mapped_data[1][:]]

	#--Similar to above.
	def in_arcs(self, node_id):
		if node_id not in self.nodes.keys():
			return []
		return self.nodes[node_id][0]

	#--Returns list of adjacent nodes on input arcs
	def in_adjacent(self, node_id):
		return [self.head(a) for a in self.in_arcs(node_id)]

	#--Returns list of adjacent nodes on output arcs
	def out_adjacent(self, node_id):
		return [self.tail(a) for a in self.out_arcs(node_id)]

	#--Returns list of adjacent nodes
	def adjacent(self, node_id):
		return self.in_adjacent(node_id) + self.out_adjacent(node_id)

	def out_adjacency_list(self):
		return dict([(node, self.out_adjacent(node)) for node in self.nodes])
		#return { node : self.out_adjacent(node) for node in self.nodes}

	#--Similar to above.
	def in_arcs_data(self, node_id):
		#mapped_data=map(None, self.nodes[node_id])
		#return [self.edge_data(edge_id) for edge_id in mapped_data[0][:]]
		return [self.edge_data(edge_id) for edge_id in self.in_arcs(node_id)]

	#--Returns a list of in and out arcs.
	def arc_list(self, node_id):
		in_list=self.in_arcs(node_id)
		out_list=self.out_arcs(node_id)
		deg_list=[]
		for arc in in_list:
			deg_list.append(arc)
		for arc in out_list:
			deg_list.append(arc)
		return deg_list

	def out_degree(self, node_id):
		return len(self.nodes[node_id][1])

	def in_degree(self, node_id):
		return len(self.nodes[node_id][0])

	def degree(self, node_id):
		mapped_data=map(None, self.nodes[node_id])
		return len(mapped_data[0])+len(mapped_data[1])

	#location of each node in topo list
	def make_topo_node_finder(self):
		index = 0
		for node in self.topological_sort():
			self.topo_loc[node] = index
			index += 1

	def topo_location(self,node):
		if len(self.topo_loc) == 0:
			self.make_topo_node_finder()
		return self.topo_loc[node]


	#--Checks if two nodes are adjacent
	#--Lazily build adjacency list if necessary
	def adjacent(self, node1_id, node2_id):
		if len(self.adjacency_list) == 0: #need to build adjacency list
			for node in self.nodes:
				ins = [self.head(x) for x in self.in_arcs(node)]
				outs = [self.tail(x) for x in self.out_arcs(node)]
				self.adjacency_list[node] = ins + outs
		return node1_id in self.adjacency_list[node2_id]
	# --- Traversals ---

	#--Performs a topological sort of the nodes by "removing" nodes with indegree 0.
	#--If the graph has a cycle, the Graph_topological_error is thrown with the
	#--list of successfully ordered nodes.
	def topological_sort(self):
		if len(self.topo_sort) > 0:
			return self.topo_sort

		topological_list=[]
		topological_queue=GraphQueue()
		indeg_nodes={}
		node_list=self.nodes.keys()
		for node in node_list:
			indeg=self.in_degree(node)
			if indeg==0:
				topological_queue.add(node)
			else:
				indeg_nodes[node]=indeg
		while not topological_queue.empty():
			current_node=topological_queue.remove()
			topological_list.append(current_node)
			out_edges=self.out_arcs(current_node)
			for edge in out_edges:
				tail=self.tail(edge)
				indeg_nodes[tail]=indeg_nodes[tail]-1
				if indeg_nodes[tail]==0:
					topological_queue.add(tail)
		#--Check to see if all nodes were covered.
		if len(topological_list)!=len(node_list):
			logging.warn( "Graph appears to be cyclic. Topological sort is invalid!")
			raise (Graph_topological_error, topological_list)

		self.topo_sort = topological_list
		return topological_list

	#--Performs a reverse topological sort by iteratively "removing" nodes with out_degree=0
	#--If the graph is cyclic, this method throws Graph_topological_error with the list of
	#--successfully ordered nodes.
	def reverse_topological_sort(self):
		topological_list=[]
		topological_queue=GraphQueue()
		outdeg_nodes={}
		node_list=self.nodes.keys()
		for node in node_list:
			outdeg=self.out_degree(node)
			if outdeg==0:
				topological_queue.add(node)
			else:
				outdeg_nodes[node]=outdeg
		while not topological_queue.empty():
			current_node=topological_queue.remove()
			topological_list.append(current_node)
			in_edges=self.in_arcs(current_node)
			for edge in in_edges:
				head_id=self.head(edge)
				outdeg_nodes[head_id]=outdeg_nodes[head_id]-1
				if outdeg_nodes[head_id]==0:
					topological_queue.add(head_id)
		#--Sanity check.
		if len(topological_list)!=len(node_list):
			raise (Graph_topological_error, topological_list)
		return topological_list

	#--Tells dfs to stop searching this branch and go on to the next one
	class SkipBranch(Exception):
		pass



	#--Returns a list of nodes in some DFS order.
	#--repeat allows it to go over the same node twice
	def dfs(self, source_id, visitor=None, repeat=False):
		nodes_already_stacked={source_id:0}
		dfs_list=[]

		dfs_stack=GraphStack()
		dfs_stack.push(source_id)

		while not dfs_stack.empty():
			current_node=dfs_stack.pop()
			dfs_list.append(current_node)
			out_edges=self.out_arcs(current_node)

			if visitor != None:
				if (visitor.discover_node(self, current_node)):
					continue #terminate search of this branch
				if out_edges == []:
					try:
						visitor.end_branch(self, current_node)
					except AttributeError:
						pass

			for edge in out_edges:
				if repeat or not nodes_already_stacked.has_key(self.tail(edge)):
					nodes_already_stacked[self.tail(edge)]=0
					dfs_stack.push(self.tail(edge))
		return dfs_list

	class Counter:
		def __init__(self, goal):
			self.count = 0
			self.goal = goal

		def discover_node(self, graph, current_node):
			if current_node == self.goal:
				self.count += 1
				return True
			else:
				return False

	def stringify(self, value):
		if type(value) is str:
			return "'" + value + "'"
		else:
			return str(value)

	#prints a python parsable dictionary representation of the graph
	def __str__(self):
		s = ['{\n\t']
		for (key,value) in self.graph_attributes.items():
			s.append("'" + key + "' : " + self.stringify(value) + ',\n\t')

		s.append("'nodes' : " + str(self.node_dict()) + ',\n\t')
		s.append("'edges' : " + str([(self.head(x), self.tail(x)) for x in self.edge_list()]) + '\n')

		s.append('}')
		return "".join(s)


	#--Returns the number of paths between two nodes.

	def paths(self, from_node, to_node):
		if from_node in self.closure:
			count = self.closure[from_node].count(to_node)
			#print 'path',from_node,'->',to_node,'=',count
			return count
		else:
			return 0

	#--Returns a list of nodes in some DFS order.
	def back_dfs(self, source_id, visitor=None):
		nodes_already_stacked={source_id:0}
		dfs_list=[]

		dfs_stack=GraphStack()
		dfs_stack.push(source_id)

		while not dfs_stack.empty():
			current_node=dfs_stack.pop()
			dfs_list.append(current_node)
			in_edges=self.in_arcs(current_node)

			if visitor != None:
				if (visitor.discover_node(self, current_node)):
					continue #terminate search of this branch
				if in_edges == []:
					try:
						visitor.end_branch(self, current_node)
					except AttributeError:
						pass

			for edge in in_edges:
				if not nodes_already_stacked.has_key(self.head(edge)):
					nodes_already_stacked[self.head(edge)]=0
					dfs_stack.push(self.head(edge))
		return dfs_list

	#--Returns a list of nodes in some BFS order.
	def bfs(self, source_id):
		nodes_already_queued={source_id:0}
		bfs_list=[]

		bfs_queue=GraphQueue()
		bfs_queue.add(source_id)

		while not bfs_queue.empty():
			current_node=bfs_queue.remove()
			bfs_list.append(current_node)
			out_edges=self.out_arcs(current_node)
			for edge in out_edges:
				if not nodes_already_queued.has_key(self.tail(edge)):
					nodes_already_queued[self.tail(edge)]=0
					bfs_queue.add(self.tail(edge))
		return bfs_list


	#--Returns a list of nodes in some BACKWARDS BFS order.
	#--Starting from the source node, BFS proceeds along back edges.
	def back_bfs(self, source_id):
		nodes_already_queued={source_id:0}
		bfs_list=[]

		bfs_queue=GraphQueue()
		bfs_queue.add(source_id)

		while not bfs_queue.empty():
			current_node=bfs_queue.remove()
			bfs_list.append(current_node)
			in_edges=self.in_arcs(current_node)
			for edge in in_edges:
				if not nodes_already_queued.has_key(self.head(edge)):
					nodes_already_queued[self.head(edge)]=0
					bfs_queue.add(self.head(edge))
		return bfs_list

	#--Enacts visitor pattern on dfs and bfs
	#--Visitor function discover_node(graph, node) is called for each node
	def dfs_visit(self, start_node, visitor):
		for node in self.dfs(start_node):
			visitor.discover_node(self, node)

	def bfs_visit(self, start_node, visitor):
		for node in self.bfs(start_node):
			if node != start_node:
				visitor.discover_node(self, node)

	#backwards dfs visitor
	def back_bfs_visit(self, start_node, visitor):
		for node in self.back_bfs(start_node):
			if node != start_node:
				visitor.discover_node(node)

	#--Returns all the root nodes of the graph
	def roots(self):
		return [x for x in self.node_list() if len(self.in_arcs(x)) == 0]

	class DummyVisitor:
		def finish(self, graph, id):
			return False

		def end_branch(self, graph, id):
			return False

		def discover(self, graph, id):
			return False

	# Algorithm extracts edges(tail_nodes) from stack:
	# 1) first  time algorithm meets node: process it + push it's out edges on stack.
	# 2) second time algorithm meets node: all children already passed (sub-tree finished)
	# if edge_id = -1, it means we got root.
	# node_id = self.tail(edge), in the case of root node, doesn't edge exist
	def dfs_edge(self, start_edge_id, node_visitor=DummyVisitor(), edge_visitor=DummyVisitor(), repeat=False):
		try:
			# nodes_already_stacked = {start_node_id:0}
			nodes_already_stacked = {}
			dfs_list  = []              # list  of edges
			dfs_stack = GraphStack()    # stack of edges

			#for edge_id in self.out_arcs(start_node_id):
			#    dfs_stack.push([edge_id, False]) # False = Children not stacked, edge not processed
			dfs_stack.push([start_edge_id, False]) # False = Children not stacked, edge not processed

			while not dfs_stack.empty():
				[edge_id, ChildrenStacked] = dfs_stack.top()
				node_id = self.tail(edge_id)

				if ChildrenStacked:     # edge passed processing + and childrent stacked = Edge finished
					edge_visitor.finish(self, edge_id)
					node_visitor.finish(self, node_id)
					dfs_stack.pop()     # delete edge
					continue

				# if we get here: edge & tail node are not processed & child edges not stacked

				dfs_list.append(edge_id)   # start processing, means add to dfs list.

				# passing on node & passing on edge. If discover return true stop search
				if ( node_visitor.discover(self, node_id) or edge_visitor.discover(self, edge_id) ):
					dfs_stack.pop() # delete edge
					continue        # no need to continue search

				dfs_stack.top()[1] = True  # set children stacked + edge processed
				if nodes_already_stacked.has_key(node_id) and not repeat: # if node already visited
					continue

				nodes_already_stacked[node_id] = 0

				# Continue search, pass on children
				out_edges = self.out_arcs(node_id)
				if len(out_edges) == 0: # no out edges
					node_visitor.end_branch(self, node_id)
					edge_visitor.end_branch(self, edge_id)

				for edge_id in out_edges:
					node_id = self.tail(edge_id)
					if repeat or not nodes_already_stacked.has_key(node_id):
						nodes_already_stacked[node_id] = 0
						dfs_stack.push([edge_id, False]) # False - means Children not stacked, edge not processed

			return dfs_list


		except:
			nodes = []
			for edge_id in dfs_list:
				Node = self.head_data(edge_id)
				nodes += Node
			msg = "Tasks passed by dfs_edge: " + str(nodes)
			logging.error(msg)
			raise



	def roots(self):
		return [x for x in self.node_list() if len(self.in_arcs(x)) == 0]


	#creates a toposort of graph partitioned into strongly connected components
	#this detects and allows for circuits
	def robust_topological_sort(self):
		#convert graph into cannonical python format
		graph = {}
		for node in self.node_list():
			graph[node] = [self.tail(x) for x in self.out_arcs(node)]

		#print 'original graph', graph
		sorted_components = robust_topological_sort(graph)
		#print 'robust topo sort', sorted_components
		return sorted_components
