import numpy as np
import sys
from math import floor
from heapq import heapify, heappop, heappush

class Lattice:
	def __init__(self, n_qid):
		self.n_qid = n_qid	  			# Number of QID
		self.hierarchies = [0] * n_qid	# List where position i containts the taxonomy tree hight of attribute i
		self.dic = []		  			# (list of list): Dictionaries for hierarchies
		self.hier = []		  			# (list of np.array): Hierarchy matrices
		self.distinct = []				# (numpy matrix): Position i,j is the number of distinct values of
										# 				  attribute i in the level of generalization j
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

	def checkPath(path, heap):
		low = 0
		high = len(path)-1
		optimum = None

		while low <= high:
			mid = floor((low+high)/2)
			node = path[mid]
			# if checkAndTag(node):
			# 	optimum = node
			# 	high = mid-1
			# else:
			# 	heap.add(node)
			# 	low = mid+1

		# store(optimum)

	def c(self, n):
		"""
			Calculates metrics to sort lattice nodes.

			c1(n): Node level
			c2(n): Precision metric: Average generalization over all quasi-identifiers
			c3(n): Average over the number of distinct values on the current level of a quasi-identifier

			@Parameters:
				n: tuple that represents a node in a lattice
			
			@Return:
				Vector [c1, c2, c3]
		"""

		c1 = sum(n) 

		sC1, sC2 = 0, 0
		for i in np.arange(len(n)):
			sC1 += (n[i]/self.hierarchies[i])
			sC2 += (self.distinct[i][n[i]]/self.distinct[i][0])

		c2 = sC1/self.n_qid
		c3 = 1 - (sC2/self.n_qid)

		return np.array([c1, c2, c3])
