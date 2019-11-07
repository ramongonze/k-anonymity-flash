import pandas as pd
import numpy as np
import lattice

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
        levelsCopy = levels.copy()
        for i in np.arange(len(levels)-1, -1, -1):
            if self.oldLevels[i] == levelsCopy[i]:
                del levelsCopy[i]

        for row in np.arange(self.buffer.shape[0]):
            for col in levelsCopy:
                self.buffer[row][col] = self.lat.hier[col][data[row][col]][levels[col]]

        self.oldLevels = levels.copy()
