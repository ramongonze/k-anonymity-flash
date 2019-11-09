import dataset
import numpy as np

def findPath(D, node, taggedNodes):
	"""
		It produces a path of untagged nodes.
		
		@Parameters:
			D: Dataset object
			node: tuple of integers
			taggedNodes: set of nodes
			
		@Return:
			path: list of nodes
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
			D: Dataset object
			k: parameter of k-anonymity
			node: tuple of integers
			taggedNodes: set of tuples
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
	
def checkPath(path, heap, k, D, optimums):
	"""
		@Parameters:
			path: list of nodes
			heap: list of tuples
			k: parameter of k-anonymity
			D: Dataset object
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
			heapq.heappush(heap, node)
			low = mid+1

	# store(optimum)
	optimums.append(optimum)

def flash(D, k):
	"""
		@Parameters:
			D: Dataset object
			k: parameter of k-anonymity
	"""

	optimums = []
	taggedNodes = set()
	latticeHeight = sum(D.lat.hierarchies)
	currLevel = [tuple([0]*D.n_qid)] # There is only the node (0,...,0) at level 0
	heap = []
	for l in np.arange(latticeHeight):
		for node in currLevel:
			if node not in taggedNodes:
				path = findPath(D, node, taggedNodes)
				checkPath(path, heap, k, D, optimums)
				while len(heap) > 0:
					node = heapq.heappop(heap)
					for up in D.lat.sortedSuccessors(node):
						if up not in taggedNodes:
							path = D.lat.findPath(up)
							checkPath(path, heap, k, D, optimums)
		
		currLevel = D.lat.nextLevel(currLevel)

	return optimums
