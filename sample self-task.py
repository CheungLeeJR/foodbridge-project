# ======================
# Task 2 - Self Study
# Data Structure: Matrix 
# Algorithm: Radix Sort
# ======================

def radix_sort(arr):
    """
    Perform radix sort on a 1D array of non-negative integers.
    Sort digit by digit from least significant to most significant.
    """
    if not arr:
        return arr

    max_num = max(arr)    # Find the maximum number to determine digit count
    exp = 1               # Current digit position: 1 for units, 10 for tens, etc.

    while max_num // exp > 0:
        buckets = [[] for _ in range(10)]  # Create 10 buckets (0-9)

        # Distribute elements into corresponding buckets
        for num in arr:
            digit = (num // exp) % 10
            buckets[digit].append(num)

        # Collect elements from buckets to form a new sorted array
        arr = []
        for bucket in buckets:
            arr.extend(bucket)

        exp *= 10  # Move to the next higher digit

    return arr


def sort_matrix_by_column(matrix, col_idx):
    """
    Sort a matrix (2D list) by values in a specified column using radix sort.
    :param matrix: input 2D list
    :param col_idx: index of the column used as sorting key
    :return: new matrix sorted by the given column
    """
    # Extract the target column as the sorting key
    column = [row[col_idx] for row in matrix]

    # Sort the column using radix sort
    sorted_col = radix_sort(column)

    # Reorder matrix rows according to the sorted column
    sorted_matrix = []
    used = [False] * len(matrix)

    for val in sorted_col:
        for i in range(len(matrix)):
            if not used[i] and matrix[i][col_idx] == val:
                sorted_matrix.append(matrix[i])
                used[i] = True
                break

    return sorted_matrix


# ======================
# Test the implementation
# ======================
if __name__ == "__main__":
    # Example matrix
    my_matrix = [
        [9, 9],
        [2, 2],
        [6, 6],
        [1, 1]
    ]

    print("Original matrix:")
    for row in my_matrix:
        print(row)

    # Sort matrix by column 0
    sorted_matrix = sort_matrix_by_column(my_matrix, col_idx=0)

    print("\nMatrix after sorting by column 0 (Radix Sort):")
    for row in sorted_matrix:
        print(row)




#  Code Example :to analyze student grades.
import numpy as np 

# A matrix representing tabular data:
# Rows: Students (Alice, Bob, Charlie, Diana)
# Columns: Subject Scores (Math, Science, History)
grades_matrix = np.array([
    [85, 92, 78],  # Alice's scores
    [89, 90, 82],  # Bob's scores
    [75, 85, 88],  # Charlie's scores
    [92, 88, 95]   # Diana's scores
])

# Target 1: Find the average score for each student (Analyze across columns for each row)
# axis=1 means we compute the mean across the columns for each individual row.
student_averages = grades_matrix.mean(axis=1)
print(f"Average score per student: {student_averages}")

# Target 2: Find the highest score in each subject (Analyze across rows for each column)
# axis=0 means we compute the max down the rows for each individual column.
highest_subject_scores = grades_matrix.max(axis=0)
print(f"Highest score per subject: {highest_subject_scores}")





# Code Example: Using a matrix as a game board for Tic-Tac-Toe.
# A matrix used as the foundational structure of a state-based program
# 3x3 Grid representing a Tic-Tac-Toe board using a List of Lists
game_board = [
    ['X', 'O', 'X'],
    ['.', 'X', 'O'],
    ['O', '.', 'X']
]

def check_diagonal_win(matrix, target_player):
    """Checks if a specific player has won on the main diagonal."""
    size = len(matrix)
    
    # We navigate the matrix using coordinate indexing: matrix[row][col]
    # For a diagonal, the row and column indices are the same (0,0 -> 1,1 -> 2,2)
    for i in range(size):
        if matrix[i][i] != target_player:
            return False
            
    return True

# Check if 'X' has won the game
is_x_winner = check_diagonal_win(game_board, 'X')
print(f"Did Player 'X' win on the diagonal? {is_x_winner}")
