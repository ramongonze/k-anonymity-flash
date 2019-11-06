import pandas as pd
import numpy as np
import lattice

class Dataset:
    
    def __init__(self, df):
        self.data = np.array([])            # (numpy matrix): Dataset with all values changed to integers
        self.dic = []                       # (list of list): Dictionaries for hierarchies
        self.hier = []                      # (list of np.array): Hierarchy matrices
        self.lat = None                     # (Lattice object): Lattice graph
        self.__DFtoInt(df)
        self.n_qid = len(self.data[0])      # (int): Number of attributes
        self.bufferData = self.data.copy()
        self.oldLevels = [0] * self.n_qid    # (list of int): Current hierarchies levels of buffer

    def createLattice(self, hierarchies):
        self.lat = lattice.Lattice(self.n_qid, hierarchies)

    def addHierarchy(self, att, values, newNames):
        """
            Add a column in 'att' hierarchy matrix and the new hierarchy names in 
            'att' dictionary.
            
            @Parameters
                att (int): attribute's index.
                values (dict): dictionary associating values from the current hierarchy level
                               to the hierarchy level+1. Obs: The association is int to int.
                newNames (list): list of new names in the hierarchy.
        """
        
        # Update hierarchy matrix
        f = np.vectorize(lambda x : values[x])
        newColumn = f(self.hier[att][:,-1])
        self.hier[att] = np.c_[self.hier[att], newColumn]
        
        # Update dictionary
        self.dic[att].append(newNames)
    
    def __DFtoInt(self, df):
        """
            Replace all values in the dataset by integers. It also creates a dictionary
            to keep the relation between the old values and the new integer values.
            Saves the new dataset in the attribute 'self.data' and the dictionary in the
            attribute 'self.dic'.
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
            self.dic.append(U)
            
            # Add a column in the hierarchy matrix
            self.hier.append(np.array([[i] for i in np.arange(len(U))]))

    def changeData(self, levels):
        """
            @Paramaters:
                levels: list of hierarchies levels to change buffer
        """

        # Discard columns that are in the same level as the previous buffer
        levelsCopy = levels.copy()
        for i in np.arange(len(levels)-1, -1, -1):
            if self.oldLevels[i] == levelsCopy[i]:
                del levelsCopy[i]

        for row in np.arange(self.buffer.shape[0]):
            for col in levelsCopy:
                self.buffer[row][col] = self.hier[col][data[row][col]][level[col]]

        self.oldLevels = levels.copy()
