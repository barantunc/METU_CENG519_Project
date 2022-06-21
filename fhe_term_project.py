from operator import mod
from eva import EvaProgram, Input, Output, evaluate, Expr
from eva.ckks import CKKSCompiler
from eva.seal import generate_keys
from eva.metric import valuation_mse
import timeit
import time
import networkx as nx
from random import random, randrange
import matplotlib.pyplot as plt
import numpy as np

# Using networkx, generate a random graph
# You can change the way you generate the graph
def generateGraph(n):
    ws = nx.path_graph(n)
    return ws

# If there is an edge between two vertices its weight is 1 otherwise it is zero
# You can change the weight assignment as required
# Two dimensional adjacency matrix is represented as a vector
# Assume there are n vertices
# (i,j)th element of the adjacency matrix corresponds to (i*n + j)th element in the vector representations
def serializeGraphZeroOne(GG,vec_size):
    n = GG.size()
    print("n:",n)
    graphdict = {}
    g = []
    for nodeindex in range(n):
    
        weight = randrange(1,10)
        
        g.append(weight)  
        key = 'p_' + str(nodeindex)+ '_' + str(nodeindex+1)
        graphdict[key] = [weight,0] # EVA requires str:listoffloat
    # EVA vector size has to be large, if the vector representation of the graph is smaller, fill the eva vector with zeros
    for i in range(vec_size - n): 
        g.append(0.0)
    print(len(g))
    return g, graphdict

# To display the generated graph
def printGraph(graph,n):
    for row in range(n):
        for column in range(n):
            print("{:.5f}".format(graph[row*n+column]), end = '\t')
        print() 

# Eva requires special input, this function prepares the eva input
# Eva will then encrypt them
def prepareInput(network_graph, m):
    
    input = {}
    graph, graphdict = serializeGraphZeroOne(network_graph,m)
    print("graphdict:",graphdict)
    print("graph:",graph)
    input['paths'] = graph
    return graphdict

# This is the dummy analytic service
# You will implement this service based on your selected algorithm
# you can other parameters using global variables !!! do not change the signature of this function 
def graphanalticprogram(graph):
    reval = graph<<1 ## Check what kind of operators are there in EVA, this is left shift
    # Note that you cannot compute everything using EVA/CKKS
    # For instance, comparison is not possible
    # You can add, subtract, multiply, negate, shift right/left
    # You will have to implement an interface with the trusted entity for comparison (send back the encrypted values, push the trusted entity to compare and get the comparison output)
    return reval

def pathsumprogram(path,nodecount,start_node_index):
    matrix = np.zeros(shape=(1,2), dtype=Expr)
    sum_left = 0
    sum_right = 0
    print(range(start_node_index,nodecount,1))
    print(range(0,start_node_index,1))

    for path_index in range(start_node_index,nodecount-1,1):
        sum_right += path[f"p_{path_index}_{path_index+1}"]
    for path_index in range(0,start_node_index-1,1):
        sum_left += path[f"p_{path_index}_{path_index+1}"]
    return sum_left,sum_right

# Do not change this 
# the parameter n can be passed in the call from simulate function
class EvaProgramDriver(EvaProgram):
    def __init__(self, name, vec_size=4, n=4):
        self.n = n
        super().__init__(name, vec_size)

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

# Repeat the experiments and show averages with confidence intervals
# You can modify the input parameters
# n is the number of nodes in your graph
# If you require additional parameters, add them
def simulate(n):
    m = 4096*4
    print("Will start simulation for ", n)
    config = {}
    config['warn_vec_size'] = 'false'
    config['lazy_relinearize'] = 'true'
    config['rescaler'] = 'always'
    config['balance_reductions'] = 'true'
    inputs = prepareInput(n, m)
    
    graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m,n=n)
    with graphanaltic:
        graph = Input('Graph')
        reval = graphanalticprogram(graph)
        Output('ReturnedValue', reval)
    
    prog = graphanaltic
    prog.set_output_ranges(30)
    prog.set_input_scales(30)

    start = timeit.default_timer()
    compiler = CKKSCompiler(config=config)
    compiled_multfunc, params, signature = compiler.compile(prog)
    compiletime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    public_ctx, secret_ctx = generate_keys(params)
    keygenerationtime = (timeit.default_timer() - start) * 1000.0 #ms
    
    start = timeit.default_timer()
    encInputs = public_ctx.encrypt(inputs, signature)
    encryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    encOutputs = public_ctx.execute(compiled_multfunc, encInputs)
    executiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    outputs = secret_ctx.decrypt(encOutputs, signature)
    decryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    reference = evaluate(compiled_multfunc, inputs)
    referenceexecutiontime = (timeit.default_timer() - start) * 1000.0 #ms
    
    # Change this if you want to output something or comment out the two lines below
    for key in outputs:
        print(key, float(outputs[key][0]), float(reference[key][0]))

    mse = valuation_mse(outputs, reference) # since CKKS does approximate computations, this is an important measure that depicts the amount of error

    return compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse 


def find_max_path_length(input_graph,n,m,start_node_index, k):
    
    print("Will start path calculation for n,m: ", n,',', m)
    config = {}
    config['warn_vec_size'] = 'false'
    config['lazy_relinearize'] = 'true'
    config['rescaler'] = 'always'
    config['balance_reductions'] = 'true'
    inputs = prepareInput(input_graph, m)
    print("inputs:",inputs)
    grap_find_max_path_length = EvaProgramDriver("grap_find_max_path_length", vec_size=m,n=n)
    with grap_find_max_path_length:
        input = {'zero': Input('zero', is_encrypted=True)}
        for i in range(n):
            key = f"p_{i}_{i+1}"
            input[key] = Input(key)
        path_sum_left,path_sum_right = pathsumprogram(input, n ,start_node_index)
        Output('path_sum_left', path_sum_left)
        Output('path_sum_right', path_sum_right)
        
    
    prog = grap_find_max_path_length
    prog.set_output_ranges(40)
    prog.set_input_scales(40)

    start = timeit.default_timer()
    compiler = CKKSCompiler(config=config)
    compiled_multfunc, params, signature = compiler.compile(prog)
    compiletime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    public_ctx, secret_ctx = generate_keys(params)
    keygenerationtime = (timeit.default_timer() - start) * 1000.0 #ms
    
    start = timeit.default_timer()
    encInputs = public_ctx.encrypt(inputs, signature)
    encryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    encOutputs = public_ctx.execute(compiled_multfunc, encInputs)
    executiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    outputs = secret_ctx.decrypt(encOutputs, signature)
    decryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    reference = evaluate(compiled_multfunc, inputs)
    referenceexecutiontime = (timeit.default_timer() - start) * 1000.0 #ms
    
    # Change this if you want to output something or comment out the two lines below
    for key in outputs:
        print(key, float(outputs[key][0]), float(reference[key][0]))

    mse = valuation_mse(outputs, reference) # since CKKS does approximate computations, this is an important measure that depicts the amount of error
    path_exist = False
    if outputs['path_sum_left'] > k or outputs['path_sum_right'] > k:
        path_exist = True
    return path_exist, compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse 

if __name__ == "__main__":
    simcnt = 1000 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    # resultfile = open("results.csv", "a")  # Measurement results are collated in this file for you to plot later on
    # resultfile.write("NodeCount,PathLength,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    # resultfile.close()
    
    #print("Simulation campaing started:")
    # for nc in range(36,64,4): # Node counts for experimenting various graph sizes
    #     n = nc
    #     print("n:",n)
    #     # resultfile = open("results.csv", "a") 
    #     for i in range(simcnt):
    #         #Call the simulator
    #         compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse = simulate(n)
    #         res = str(n) + "," + str(i) + "," + str(compiletime) + "," + str(keygenerationtime) + "," +  str(encryptiontime) + "," +  str(executiontime) + "," +  str(decryptiontime) + "," +  str(referenceexecutiontime) + "," +  str(mse) + "\n"
    #         # print(res)
    #         # resultfile.write(res)
    #     # resultfile.close()

    
    
    
    n = 9 #node count
    m = 2
    start_node_index = 2
    GG = generateGraph(n)
    output = find_max_path_length(GG,n,m,start_node_index)
    print("output:", output)

    nx.draw(GG)
    plt.savefig('graph_'+str(time.time())+'.png')

            