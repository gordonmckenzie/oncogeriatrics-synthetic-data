import numpy as np

arr = np.array([31.5,9,1.3])

arr_sum = 1 / np.sum(arr)

final = arr_sum * arr

final_r = np.around(final, decimals=3)

#assert np.sum(final_r) == 1.0
print(np.sum(final_r))
print(final_r)