import numpy as np
import matplotlib.pyplot as plt

file = open("519ProjectTemplate/results.csv")
numpy_array = np.loadtxt(file, delimiter=",")
counter = 0
#["NodeCount","PathLength","SimCnt","Average CompileTime","KeyGenerationTime","EncryptionTime","ExecutionTime","DecryptionTime","ReferenceExecutionTime","Mse"]
mean_results_list = []
max_results_list = []
min_results_list = []
NodeCount = 0
Nodes_list = []
#find nodes used
for row in numpy_array:
    if NodeCount != row[0]:
        Nodes_list.append(row[0])
        NodeCount = row[0]

#print(Nodes_list)
for nodes in Nodes_list:
    #print(numpy_array[numpy_array[:,0] == nodes][0])
    filtered_np_array = numpy_array[numpy_array[:,0] == nodes]
    mean_results = np.mean(filtered_np_array[:, [3, 4, 5, 6, 7, 8]], axis=0)
    max_results = np.max(filtered_np_array[:, [3, 4, 5, 6, 7, 8]], axis=0)
    min_results = np.min(filtered_np_array[:, [3, 4, 5, 6, 7, 8]], axis=0)
    mean_results_list.append(mean_results.tolist())
    max_results_list.append(max_results.tolist())
    min_results_list.append(min_results.tolist())

print(max_results_list)


fig = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,0].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,0].ravel(), np.array(max_results_list)[...,0].ravel()))).T

plt.title("Average Compile Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

fig2 = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,1].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,1].ravel(), np.array(max_results_list)[...,1].ravel()))).T

plt.title("Average Key Generation Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

fig3 = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,2].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,2].ravel(), np.array(max_results_list)[...,2].ravel()))).T

plt.title("Average Encryption Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

fig4 = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,3].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,3].ravel(), np.array(max_results_list)[...,3].ravel()))).T

plt.title("Average Execution Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

fig5 = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,4].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,4].ravel(), np.array(max_results_list)[...,4].ravel()))).T

plt.title("Average Decryption Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

fig6 = plt.figure()
x = Nodes_list
y = np.array(mean_results_list)[...,5].ravel()

y_error = np.array(list(zip(np.array(min_results_list)[...,5].ravel(), np.array(max_results_list)[...,5].ravel()))).T

plt.title("Average Reference Time (ms) vs NodeCount ")
plt.errorbar(x, y, yerr=y_error,fmt='o', solid_capstyle='butt',markersize=8,capsize=3 , label='1000 runs')
plt.legend(loc='upper right')
plt.xticks(x)

plt.show()
