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
	
	# Binary search
	def bSearch(self, arr, key):
		i, j = 0, len(arr)-1
		while i <= j:
			m = (i+j)//2
			if key <= arr[m]:
				j = m-1
			else:
				i = m+1
		if i == 0 and arr[0] > key:
			return None
		return i


	def createNumericalHierarchies(self, att, h):
		"""
			Given an interval this function produces a taxonomy tree.

			@Parameters:
				att (int): Attribute index
				h: Desired taxonomy tree height. h >= 2

			@Return:
				hierarchies: Matrix
				dic: dict with the relationship between intervals and integers		
		"""

		dic = {}
		Min, Max = self.dic[att][0], self.dic[att][-1] # Interval bounds
		intervals = [(Min,(Min+Max)//2,Max)] # Initial interval: Entire range of values
		nextLevel = len(self.dic[att])-1 + 2**(h-1) -2
		dic = ['*']
		hierarchies = np.array([[nextLevel+1]]*len(self.dic[att]))
		for _ in np.arange(h-2):
			newH, nextIntervals = [], []
			while len(intervals) > 0:
				it = intervals.pop(0) # Extract the first element
				
				# Add the new 2 levels in the dictionary
				if it[2] == Max:
					dic.append('[%.2f, %.2f]'%(it[1], it[2]))
				else:
					dic.append('[%.2f, %.2f)'%(it[1], it[2]))
				dic.append('[%.2f, %.2f)'%(it[0], it[1]))
				
				# Binary search to find index in self.dic with value >= it[1]
				low = self.bSearch(self.dic[att], it[0])
				mid = self.bSearch(self.dic[att], it[1]) 
				up = self.bSearch(self.dic[att], it[2])
				if it[2] != Max:
					up -= 1
				newH += ([[nextLevel]] * (up-mid+1))
				newH += ([[nextLevel]] * (mid-low)) # Interval oppened in right side

				# Queue the next 2 subintervals
				nextIntervals.append((it[1],(it[1]+it[2])//2,it[2]))
				nextIntervals.append((it[0],(it[0]+it[1])//2,it[1]))

				# newH += ([[nextLevel-1]] * (it[1]-it[0]))
				# newH += ([[nextLevel]] * (it[2]-it[1]))
				# if it[2] == maxInterval:
				# 	newH += [[nextLevel]]

				nextLevel -= 2

			intervals = nextIntervals
			hierarchies = np.c_[np.array(newH), hierarchies]

		return hierarchies, dic[::-1]

	def addNewHierarchy(self, att, values, newNames, numerical=False):
		"""
			Add a column in 'att' hierarchy matrix and the new hierarchy names in 
			'att' dictionary.
			
			@Parameters
				att (int): attribute's index.
				values: if numerical=True, values must be a 2d matrix
						if numerical=False, values must be a dictionary associating values 
						from the current hierarchy level to the hierarchy level+1.
						Obs: The association is int to int.
				newNames (list): list of new names in the hierarchy.
				numerical: Indicates if the attribute is numerical or not. If it is numerical,
						   the function expects the entire hierarchy matrix (get from frunction
						   'createNumericalHierarchies').
		"""
		
		if numerical:
			self.hierarchies[att] = values.shape[1]

			# Append new columns to self.hier matrix
			self.hier[att] = np.c_[self.hier[att], values]

			# Add the number of distinct values in the new hierarchy
			self.distinct[att]+= [2**i for i in range(self.hierarchies[att]-1,-1,-1)]
		else:
			# Increase taxonomy tree height of attribute 'att'
			self.hierarchies[att] += 1

			# Update hierarchy matrix
			f = np.vectorize(lambda x : values[x])
			newColumn = f(self.hier[att][:,-1])

			# Append a new column to self.hier matrix
			self.hier[att] = np.c_[self.hier[att], newColumn]

			# Add the number of distinct values in the new hierarchy
			self.distinct[att].append(len(newNames))

		# Update dictionary
		self.dic[att] += newNames

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
				nodes.append((self.nodeMetrics(node), tuple(node)))
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

	def predecessors(self, node):
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
		nodeM = [(self.nodeMetrics(node), node) for node in nextLevel]
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
