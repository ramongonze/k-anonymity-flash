import dataset
import numpy as np
from math import floor
from heapq import heapify, heappop, heappush

def findPath(node, D, taggedNodes):
	"""
		It produces a path of untagged nodes from a start node to the node at
		the highest level of a lattice.
		
		@Parameters:
			node: tuple of integers.
			D: Dataset object.
			taggedNodes: set of nodes.
			
		@Return:
			path: list of tuple (nodes).
	"""
	
	path = []
	while len(path) == 0 or path[-1] != node:
		path.append(node)
		for up in D.lat.sortedSuccessors(node):
			if up not in taggedNodes:
				node = up
				break
				
	return path

def checkAndTag(node, k, D, taggedNodes):
	"""
		@Parameters:
			D: Dataset object.
			k: parameter of k-anonymity.
			node: tuple of integers.
			taggedNodes: set of tuples (nodes).

		@Return:
			True if 'node' is k-anonymous.
			False if 'node' is not k-anonymous.
	"""

	anonymous = D.isKAnonymous(k, node)
	
	if anonymous:
		f = D.lat.successors
	else:
		f = D.lat.predecessors

	L = [node]
	while len(L) > 0:
		up = L.pop(0)
		if up not in taggedNodes:
			taggedNodes.add(up)
			L += f(up)

	return anonymous
	
def checkPath(path, heap, k, D, optimums, taggedNodes):
	"""
		@Parameters:
			path: list of tuples (nodes).
			heap: list of tuples (nodes).
			k: parameter of k-anonymity.
			D: Dataset object.
	"""

	low = 0
	high = len(path)-1
	optimum = None

	while low <= high:
		mid = floor((low+high)/2)
		node = path[mid]
		
		if checkAndTag(node, k, D, taggedNodes):
			optimum = node
			high = mid-1
		else:
			heappush(heap, node)
			low = mid+1

	if optimum != None:
		optimums.append(optimum)

def flash(D, k):
	"""
		Given a dataset D and a parameter k the Flash algorithm searches in the dataset
		lattice and return a list of k-anonymous nodes.

		@Parameters:
			D: Dataset object.
			k: parameter of k-anonymity.

		@Return:
			List of tuples (nodes).
	"""

	optimums = []
	taggedNodes = set()
	latticeHeight = sum(D.lat.hierarchies)
	currLevel = [tuple([0]*D.n_qid)] # There is only the node (0,...,0) at level 0
	heap = []
	for l in np.arange(latticeHeight):
		for node in currLevel:
			if node not in taggedNodes:
				path = findPath(node, D, taggedNodes)
				checkPath(path, heap, k, D, optimums, taggedNodes)
				
				while len(heap) > 0:
					node = heappop(heap)
					for up in D.lat.sortedSuccessors(node):
						if up not in taggedNodes:
							path = findPath(up, D, taggedNodes)
							checkPath(path, heap, k, D, optimums, taggedNodes)
		
		currLevel = D.lat.nextLevel(currLevel)

	return optimums
