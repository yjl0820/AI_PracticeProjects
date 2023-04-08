############################################################
# Imports
############################################################

from copy import deepcopy
from queue import Queue


############################################################
# Section 1: Sudoku
############################################################

def sudoku_cells():
    #returns the list of all cells in a Sudoku puzzle as (row, column) pairs.
    return [(row,column) for row in range(9) for column in range(9)]
    pass

def sudoku_arcs():
    #returns the list of all arcs between cells in a Sudoku puzzle corresponding to inequality constraints. (each arc should be a pair of cells whose values != in a solved puzzle)
    ##order does not matter
    arcs = []
    for rowcol1 in sudoku_cells():
        for rowcol2 in sudoku_cells():
            if rowcol1 != rowcol2:
                if (rowcol1[0] == rowcol2[0] or rowcol1[1] == rowcol2[1]) or (int(rowcol1[0]/3) == int(rowcol2[0]/3) and int(rowcol1[1]/3) == int(rowcol2[1]/3)):
                    arcs.append((rowcol1,rowcol2))
    return arcs  #should be represented a two-tuples of cells, where cells themselves are (row, column) pairs.
    pass

def read_board(path):
    #reads the board specified by the file at thegiven path and returns it as a dictionary
    #puzzles represented textually as 9 lines of 9 characters each
    # digit between "1" and "9" denotes a cell containing a fixed value
    # asterisk "*" denotes a blank cell that could contain any digit
    file = open(path, 'r')
    board_dic = {}
    for rows, line in enumerate(file): #('0','821*****7')
        for column, item in enumerate(line): #('0','8'),('1','2'),..('8','7')
            rowcol = (rows, column)
            if item == "*":
                board_dic[rowcol] = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            elif item.isdigit() :
                board_dic[rowcol] = {int(item)}
    file.close()
    return board_dic
    pass

class Sudoku(object):

    CELLS = sudoku_cells() #creates a class-level constant Sudoku. More efficient.
    ARCS = sudoku_arcs() #creates a class-level constant Sudoku

    def __init__(self, board):
        self.board = board
        pass

    def get_values(self, cell):
        return self.board[cell]
        pass

    def remove_inconsistent_values(self, cell1, cell2):
        #removes any value in the set of possibilities
        # for cell1 for which there are no values in the set of possibilities for cell2
        board = self.board
        set1 = board[cell1]
        set2 = board[cell2]

        if len(set2) == 1:
            val = list(set2)[0]
            if val in set1:
                new_set = set()
                set1_li = list(set1)
                for x in set1_li: ## for values in list of set 1, if it's also in set2 it should continue, or else add it to a new set.
                    if x == val:
                        continue
                    new_set.add(x)
                board[cell1] = new_set
                return True #If any values were removed, return True
        else: # else, return False .
            return False
        pass

    def adjacent(self, cell, j={}):
        return [k for k, i in self.ARCS if (i == cell and not j == k)]

    def finished(self):
        for cell in self.CELLS:
            if len(self.board[cell]) != 1:
                return False
        return True


    def infer_ac3(self):#narrow down each cell's set of values as much as possible
        queues = Queue()
        for arcs in self.ARCS:
            queues.put(arcs)

        while not queues.empty():
            (cell1, cell2) = queues.get()
            if self.remove_inconsistent_values(cell1, cell2):
                for k in self.adjacent(cell1, cell2):
                    queues.put((k, cell1))
        pass


    def infer_improved(self):# 7 appears after the improved in the example.
        #improved version of infer_ac3 - use loop
        pin = True
        while pin:
            self.infer_ac3()
            pin = False
            for cell in Sudoku.CELLS:
                temp_set = self.board[cell]

                if (len(temp_set) > 1):
                    for val in temp_set:
                        test_col = [self.board[(i, cell[1])] for i in range(9) if (i, cell[1]) != cell]
                        test_row = [self.board[(cell[0], i)] for i in range(9) if (cell[0], i) != cell]
                        test_block = []

                        for i in range(9):
                            for j in range(9):
                                if (i, j) != cell and (i // 3 == cell[0] // 3) and (j // 3 == cell[1] // 3):
                                    test_block.append(self.board[(i, j)])

                        column = {values for sets in test_col for values in sets}
                        row = {values for sets in test_row for values in sets}
                        block = {values for sets in test_block for values in sets}

                        if (val not in column) or (val not in row) or (val not in block):
                            self.board[cell] = {val}
                            pin = True
                            continue
        pass

    def infer_with_guessing(self):
        #call infer_improved
        self.infer_improved()

        for cell in Sudoku.CELLS:
            temp_set = self.board[cell]
            if len(temp_set) > 1:
                guess_board = deepcopy(self.board)

                for val in temp_set:
                    self.board[cell] = {val}
                    self.infer_with_guessing()
                    if self.finished():
                        break
                    else:
                        self.board = guess_board
        pass
