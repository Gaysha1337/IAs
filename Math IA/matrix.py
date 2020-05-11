import numpy as np
np.set_printoptions(suppress=True)

def print_equation(matrix: np.array, section: str):
    print("The equation for the", section, "function: ")
    print(" ".join([str(np.format_float_positional(val[0],precision=7)) + "x^" + str((i)) for i,val in enumerate(matrix[::-1])]))

# The matrix 6x6 matrix for the bottom function
X_1 = np.array([
    [11163.45,1730.77,268.34,41.60,6.45,1],
    [48426.22,5598.41,647.21,74.82,8.65,1],
    [259374.25,21435.89,1771.56,146.41,12.1,1],
    [1022622.44,64235.08,4034.87,253.45,15.92,1],
    [4312707.17,203142.12,9568.63,450.71,21.23,1],
    [6750113.53,290702.56,12519.49,539.17,23.22,1]
])

# The matrix 6x6 matrix for the top function
X_2 = np.array([
    [6750113.53,290702.56,12519.49,539.17,23.22,1],
    [11233378.26,436926.42,16994.42,661.00,25.71,1],
    [27049073.52,882514.63,28793.30,939.42,30.65,1],
    [40762799.65,1225211.89,36826.33,1106.89,33.27,1],
    [48946855.48,1418338.32,41099.34,1190.94,34.51,1],
    [53886400.63,1531733.96,43539.91,1237.63,35.18,1]
])

# These matrices are 1x6, but they should be 6x1, so they need to be transposed
Y_1, Y_2 = np.array([[4.55,6.2,7.73,7.1,4.79,4.58]]).transpose(), np.array([[4.58,4.41,4.41,4.37,4.58,4.75]]).transpose()

# The vector solutions to the matrices
X_1_Y_VALS, X_2_Y_VALS = np.linalg.solve(X_1,Y_1), np.linalg.solve(X_2,Y_2)

print_equation(X_1_Y_VALS, "Bottom")
print_equation(X_2_Y_VALS, "Top")

