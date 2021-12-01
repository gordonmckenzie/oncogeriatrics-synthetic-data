import numpy as np

[13.75,
6.01,
1.62,
6.06,
9.24,
8.64,
3.20,
47.28]

arr = np.array([13.75,
6.01,
1.62,
6.06,
9.24,
8.64,
3.20,
47.28])

arr_sum = 1 / np.sum(arr)

final = arr_sum * arr

final_r = np.around(final, decimals=3)

#assert np.sum(final_r) == 1.0
print(np.sum(final_r))
print(final_r)