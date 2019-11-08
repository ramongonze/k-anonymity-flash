import numpy as np
import sys
from math import floor
from heapq import heapify, heappop, heappush

class Lattice:
	def __init__(self, n_qid):
		self.n_qid = n_qid	  			# (int): Number of QID
		self.hierarchies = [0] * n_qid	# (list): List where position i containts the taxonomy tree hight of attribute i
		self.dic = []		  			# (list of list): Dictionaries for hierarchies
		self.hier = []		  			# (list of np.array): Hierarchy matrices
		self.distinct = []				# (numpy matrix): Position i,j is the number of distinct values of
										#				  attribute i in the level of generalization j
	def addNewHierarchy(self, att, values, newNames):
		"""
			Add a column in 'att' hierarchy matrix and the new hierarchy names in 
			'att' dictionary.
			
			@Parameters
				att (int): attribute's index.
				values (dict): dictionary associating values from the current hierarchy level
							   to the hierarchy level+1. Obs: The association is int to int.
				newNames (list): list of new names in the hierarchy.
		"""
		
		# Increase taxonomy tree height of attribute 'att'
		self.hierarchies += 1

		# Update hierarchy matrix
		f = np.vectorize(lambda x : values[x])
		newColumn = f(self.hier[att][:,-1])
		self.hier[att] = np.c_[self.hier[att], newColumn]
		
		# Update dictionary
		self.dic[att].append(newNames)

		# Add the number of distinct values in the new hierarchy
		self.distinct[att].append(len(newNames))

	def sortedSuccessors(self, node):
		"""
			Produces a list of sorted (by metrics c1,c2 and c3) successors of a node.
			
			@Parameters:
				node: tuple of integers
				
			@Return:
				nodes: list of tuples
		"""
		
		nodes = []
		node = list(node)
		for i in np.arange(len(node)):
			if node[i] < self.hierarchies[i]:
				node[i] += 1
				nodes.append((nodeMetrics(node), tuple(node)))
				node[i] -= 1
		
		nodes.sort()

		return [t[1] for t in nodes]

	def successors(self, node):
		"""
			Produces a list of successors of a node.
			
			@Parameters:
				node: tuple of integers
				
			@Return:
				nodes: list of tuples
		"""
		
		nodes = []
		node = list(node)
		for i in np.arange(len(node)):
			if node[i] < self.hierarchies[i]:
				node[i] += 1
				nodes.append(tuple(node))
				node[i] -= 1
		
		return nodes

	def predecessors(node):
		"""
			Produces a list of predecessors of a node

			@Parameters: 
				node: tuple of integers
		"""
		nodes = []
		node = list(node)
		for i in np.arange(len(node)):
			if node[i] > 0:
				node[i] -= 1
				nodes.append(tuple(node))
				node[i] += 1

		return nodes

	def nextLevel(self, nodes):
		"""
			Given a set of nodes in the lattice level L, this function is a generator
			that produces a set of nodes in the level L+1.
			
			@Parameters:
				nodes: list of nodes in the current level
		"""
		
		nextLevel = set()
		for node in nodes:
			# Look for node successors
			node = list(node)
			for i in np.arange(len(node)):
				if node[i] < self.hierarchies[i]:
					node[i] += 1
					nextLevel.add(tuple(node))
					node[i] -= 1
		
		# Sort nodes according to metrics c1, c2 and c3
		nodeM = [(nodeMetrics(node), node) for node in nextLevel]
		nodeM.sort()

		return [t[1] for t in nodeM]

	def nodeMetrics(self, n):
		"""
			Calculates metrics to sort lattice nodes.

			c1(n): Node level
			c2(n): Precision metric: Average generalization over all quasi-identifiers
			c3(n): Average over the number of distinct values on the current level of a quasi-identifier

			@Parameters:
				n: tuple that represents a node in a lattice
			
			@Return:
				Tuple (c1, c2, c3)
		"""

		c1 = sum(n) 

		sC1, sC2 = 0, 0
		for i in np.arange(len(n)):
			sC1 += (n[i]/self.hierarchies[i])
			sC2 += (self.distinct[i][n[i]]/self.distinct[i][0])

		c2 = sC1/self.n_qid
		c3 = 1 - (sC2/self.n_qid)

		return (c1, c2, c3)
