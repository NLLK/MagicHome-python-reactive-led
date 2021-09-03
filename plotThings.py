import numpy as np
import matplotlib.pyplot as plt
import time
x = np.random.randint(low=1, high=11, size=50)
y = x + np.random.randint(1, 5, size=x.size)
data = x
 
fig, ax2 = plt.subplots(
    nrows=1, ncols=1,
    figsize=(8, 4)
)
 
# ax1.scatter(x=x, y=y, marker='o', c='r', edgecolor='b')
# ax1.set_title('Scatter: $x$ versus $y$')
# ax1.set_xlabel('$x$')
# ax1.set_ylabel('$y$')
 
ax2.hist(
    data, bins=np.arange(0, 44.1),
    label=('fq', 'v')
)
plt.show()

for i in range(0,2000):
    data =+1
    plt.show()
