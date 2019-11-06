import numpy as np
import sys

class Lattice:
	def __init__(self, n_qid, hierarchies):
		self.n_qid = n_qid				  # Number of QID
		self.hierarchies = hierarchies[:] # Vector where position i containts the taxonomy tree hight of attribute i
		
	def successors(node):
		"""
			Produces a set of sucessor nodes of node given in the first parameter.
			
			@Parameters:
				node: list of integers
				hierarchies: list where position i is the taxonomy tree hight of attribute i
				
			@Return:
				nodes: set of tuples
		"""
		
		nodes = set()
		node = list(node)
		for i in np.arange(len(node)):
			if node[i] < self.hierarchies[i]:
				node[i] += 1
				nodes.add(tuple(node))
				node[i] -= 1
		return nodes

	def genSuccessors(node):
		"""
			It is a generator that produces a list of successors of a node.
			
			@Parameters:
				node: list of integers
				hierarchies: list where position i is the taxonomy tree hight of attribute i
		"""
		
		node = list(node)
		for i in np.arange(len(node)):
			if node[i] < self.hierarchies[i]:
				node[i] += 1
				yield tuple(node)
				node[i] -= 1

	def nextLevel(nodes):
		"""
			Given a set of nodes in the lattice level L, this function is a generator
			that produces a set of nodes in the level L+1.
			
			@Parameters:
				nodes: list of nodes in the current level
				hierarchies: list where position i is the taxonomy tree hight of attribute i
		"""
		
		nextLevel = set()
		for node in nodes:
			nextLevel.add(successors(node))
		
		return nextLevel

	def findPath(node, taggedNodes):
		"""
			It produces a path of untagged nodes.
			
			@Parameters:
				node: tuple of integers
				taggedNodes: set of nodes
				
			@Return:
				path: list of nodes
		"""
		
		path = []
		while len(path) == 0 or path[-1] != node:
			path.append(node)
			for up in genSuccessors(node):
				if up not in taggedNodes:
					node = up
					break
					
		return path
