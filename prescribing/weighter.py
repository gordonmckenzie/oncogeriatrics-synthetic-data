import numpy as np

arr = np.array([39.6,41.8,11.9,6.7])

arr_sum = 1 / np.sum(arr)

final = arr_sum * arr

final_r = np.around(final, decimals=3)

#assert np.sum(final_r) == 1.0
print(np.sum(final_r))
print(final_r)