import dataset
import lattice
import numpy as np
import pandas as pd
from heapq import heapify, heappop, heappush

def flash(D):
	"""
		@Parameters:
			D: Dataset object
	"""

	taggedNodes = set()
	latticeHeight = sum(D.lat.hierarchies)
	currLevel = {tuple([0]*D.n_qid)} # There is only the node (0,...,0) at level 0
	heap = []
	for l in np.arange(latticeHeight):
		for node in currLevel:
			if node not in taggedNodes:
				path = D.lat.findPath(node, taggedNodes)
				checkPath(path, heap)
				while len(heap) > 0:
					node = heapq.heappop(heap)
					for up in D.lat.genSuccessors(node):
						if up not in taggedNodes:
							path = D.lat.findPath(up)
							checkPath(path, heap)
		currLevel = D.lat.nextLevel(currLevel)
