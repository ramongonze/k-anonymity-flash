import pandas as pd
import numpy as np
import lattice
from math import log2, ceil

class Dataset:
	
	def __init__(self, df):
		"""
			@Parameters:
				df: Pandas DataFrame
		"""

		self.data = np.array([])                	# (numpy matrix): Dataset with all values changed to integers.
		self.n_qid = df.shape[1]                	# (int): Number of quasi-identifiers.
		self.lat = lattice.Lattice(self.n_qid)  	# (Lattice object): Lattice graph
		self.__convertDFToInt(df)
		self.buffer = self.data.copy()          	# (numpy matrix): Buffer used to keep self.data changed to 
													#				  different hierarchies.
		self.oldLevels = [0] * self.n_qid       	# (list of int): Current hierarchies levels of 'self.buffer'.
		self.columnsNames = list(df.columns.copy())	# (list of strings): List of attribute names

	def __convertDFToInt(self, df):
		"""
			Replace all values in the dataset by integers. It also creates a dictionary
			to keep the relation between the old values and the new integer values.
			It saves the new dataset in the attribute 'self.data' and the dictionary in the
			attribute 'self.lat.dic'.

			@Parameters:
				df: Pandas DataFrame
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

	def transformBufferData(self, node):
		"""
			Given a node from lattice, this function replaces the values of an attribute by their
			corresponding values in another hierarchy level, according to the hierarchy levels in the
			parameter.

			@Paramaters:
				node: list of hierarchy levels.
		"""

		# Discard columns that are in the same level as the previous buffer
		indexes = []
		for i in np.arange(len(node)-1, -1, -1):
			if self.oldLevels[i] != node[i]:
				indexes.append(i)

		for row in np.arange(self.buffer.shape[0]):
			for col in indexes:
				self.buffer[row][col] = self.lat.hier[col][self.data[row][col]][node[col]]

		self.oldLevels = node[:]

	def isKAnonymous(self, k, node):
		"""
			Check if the dataset is k-anonymous in the hierarchy levels given by the
			parameter node.

			@Parameters:
				k: integer.
				node: tuple of integers.

			@Return:
				True if self.buffer is k-anonymous.
				False if self.buffer is not k-anonymous.
		"""

		# Transform self.buffer
		self.transformBufferData(node)

		_, countElements = np.unique(self.buffer, return_counts=True, axis=0)
		for c in countElements:
			# If the number of distinct elements of a group is < k, the data is not k-anonymous
			if c < k:
				return False

		return True

	def generateNewDataset(self, node):
		"""
			Given a node from the lattice, replace the original values from 
			the dataset by the respectively general values accordin to node.

			@Parameters:
				node: tuple of integers

			@Return: Pandas DataFrame
		"""

		newDF = pd.DataFrame()
		for i in np.arange(self.data.shape[0]):
			newDF[i] = [self.lat.dic[att][self.lat.hier[att][self.data[i][att]][node[att]]] for att in np.arange(self.n_qid)]

		return newDF
