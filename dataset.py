import pandas as pd
import numpy as np
import lattice
from math import log2, ceil

class Dataset:
	
	def __init__(self, df):
		self.data = np.array([])                # (numpy matrix): Dataset with all values changed to integers
		self.n_qid = df.shape[1]                # (int): Number of attributes
		self.lat = lattice.Lattice(self.n_qid)  # (Lattice object): Lattice graph
		self.__DFtoInt(df)
		self.buffer = self.data.copy()          # (numpy matrix): Buffer used when changing the original dataset with different hiearchies levels
		self.oldLevels = [0] * self.n_qid       # (list of int): Current hierarchies levels of buffer
	
	def __DFtoInt(self, df):
		"""
			Replace all values in the dataset by integers. It also creates a dictionary
			to keep the relation between the old values and the new integer values.
			It saves the new dataset in the attribute 'self.data' and the dictionary in the
			attribute 'self.lat.dic'.
		"""
		
		f = np.vectorize(lambda x: dic[x])

		for col in np.arange(len(df.columns)):
			U = sorted(df.iloc[:,col].unique())

			# Create a dictionary to relate old attributes values and integers
			dic = {}
			for i in np.arange(len(U)):
				dic[U[i]] = i

			# Replace old values by integers
			if col == 0:
				self.data = f(df.iloc[:,col])
			else:
				self.data = np.c_[self.data, f(df.iloc[:,col])]

			# Link column and integer dictionary
			self.lat.dic.append(U)
			
			# Add a column in the hierarchy matrix
			self.lat.hier.append(np.array([[i] for i in np.arange(len(U))]))

			# Add the number of distinct values in level 0 of generalization
			self.lat.distinct.append([len(U)])

	def changeData(self, levels):
		"""
			@Paramaters:
				levels: list of hierarchies levels to change buffer
		"""

		# Discard columns that are in the same level as the previous buffer
		indexes = []
		for i in np.arange(len(levels)-1, -1, -1):
			if self.oldLevels[i] != levels[i]:
				indexes.append(i)

		for row in np.arange(self.buffer.shape[0]):
			for col in indexes:
				self.buffer[row][col] = self.lat.hier[col][data[row][col]][levels[col]]

		self.oldLevels = levels.copy()

	def isKAnonymous(self, k, node):
		"""
			@Parameters:
				k: integer
				node: tuple of integer

			@Return: bool
		"""

		# Transform self.buffer
		self.changeData(node)

		# Run through the powerset of attributes, starting from
		# subsets of size one, two, ..., #attributes
		bitMask = 0
		for setSize in np.arange(1,self.n_qid+1):
			n = 1
			bitMask = bitMask | 1
			limit = 1 << (self.n_qid-setSize)
			while not (bitMask & limit):
				# Select columns to make a groupby in the buffer
				bitString = bin(bitMask)[2:]
				columns = []
				for i in len(bitString):
					if bitString[i] == '1':
						columns.append(i)
				
				# Check if there is at least k elements in the groupby of 'columns'
				# If yes, the buffer is not k-anonymous
				_, countElements = np.unique(self.buffer[:,columns], return_counts=True, axis=0)
				for c in countElements:
					# If the number of distinct elements of a group is < k, the data is not k-anonymous
					if c < k:
						return False

				bitMask = (bitMask ^ (1 << (n-1))) | (1 << n)
				n += 1

		return True
