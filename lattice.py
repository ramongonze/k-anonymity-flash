import numpy as np
import sys

class Lattice:
	def __init__(self, n_qid, hierarchies):
		self.n_qid = n_qid				# Number of QID
		self.hierarchies = hierarchies  # Vector where position i containts the taxonomy tree hight of attribute i
		self.adj = {}					# Adjacent list (graph)
		self.__createLattice()			# Create the graph

	def __addEdges(self, curVertex):
		self.adj[tuple(curVertex)] = []
		curVertexModified = curVertex.copy()
		for i in np.arange(self.n_qid):
			if curVertex[i] < self.hierarchies[i]:
				curVertexModified[i] += 1
				self.adj[tuple(curVertex)].append(tuple(curVertexModified))
		
				if tuple(curVertexModified) not in self.adj:
					self.__addEdges(curVertexModified)
				curVertexModified[i] -= 1

	def __createLattice(self):
		n_nodes = 1
		for hight in self.hierarchies:
			n_nodes *= (hight+1)

		sys.setrecursionlimit(max(n_nodes, 10**4))
		self.__addEdges([0] * self.n_qid) # Initial state = [0, ..., 0]
