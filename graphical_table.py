import pandas as pd
import networkx as nx
import discretizer

def read_dataset(data_path):
	"""
	input:
		data_path: String, the path to `xx.csv`
	output:
		Pandas.DataFrame
	"""
	data = pd.read_csv(data_path)
	data = data.drop("d3mIndex",axis=1)    # drop id
	data = data.drop("TBG",axis=1)    # drop empty column

	# 1. convert 
	data["sex"] = data["sex"].str.replace("F", "0")
	data["sex"] = data["sex"].str.replace("M", "1")
	data.replace(to_replace="f", value="0", inplace=True)
	data.replace(to_replace="t", value="1", inplace=True)
	data["referral_source"] = data["referral_source"].str.replace("other", "0")
	data["referral_source"] = data["referral_source"].str.replace("SVI", "1")
	data["referral_source"] = data["referral_source"].str.replace("SVHC", "2")
	data["referral_source"] = data["referral_source"].str.replace("STMW", "3")
	data["referral_source"] = data["referral_source"].str.replace("SVHD", "4")

	# discretize
	# data["age"] = discretizer.discretize(data["age"],num_bins=5,by='frequency', labels=["age1","age2","age3","age4","age5"])
	# data["TSH"] = discretizer.discretize(data["TSH"],num_bins=5,by='frequency', labels=["TSH1","TSH2","TSH3","TSH4","TSH5"])
	# data["T3"] = discretizer.discretize(data["T3"],num_bins=5,by='frequency', labels=["T3_1","T3_2","T3_3","T3_4","T3_5"])
	# data["TT4"] = discretizer.discretize(data["TT4"],num_bins=5,by='frequency', labels=["TT4_1","TT4_2","TT4_3","TT4_4","TT4_5"])
	# data["T4U"] = discretizer.discretize(data["T4U"],num_bins=5,by='frequency', labels=["T4U_1","T4U_2","T4U_3","T4U_4","T4U_5"])
	# data["FTI"] = discretizer.discretize(data["FTI"],num_bins=5,by='frequency', labels=["FTI_1","FTI_2","FTI_3","FTI_4","FTI_5"])

	data["age"] = discretizer.discretize(data["age"],num_bins=5,by='frequency')
	data["TSH"] = discretizer.discretize(data["TSH"],num_bins=5,by='frequency')
	data["T3"] = discretizer.discretize(data["T3"],num_bins=5,by='frequency')
	data["TT4"] = discretizer.discretize(data["TT4"],num_bins=5,by='frequency')
	data["T4U"] = discretizer.discretize(data["T4U"],num_bins=5,by='frequency')
	data["FTI"] = discretizer.discretize(data["FTI"],num_bins=5,by='frequency')

	return data



def make_graph(data):
	"""
	input:
		data: Pandas.DataFrame
			contains numerical categorical data, might has nan
	node types:
		- row: 
		- column
		- categorical: the categorical value of the cell
		- cell
	"""
	graph = nx.Graph()

	# 1. every row to node
	for i in range(len(data)):
	    graph.add_node("row_"+ str(i), type="row") # id format "row_id"

	column_counter = 0
	for column_name in data:
	    col = data[column_name]
	    graph.add_node(column_name, type="column") # 2. every column to node, id format "name"
	    # 3. each categorical value in this column, id format "name-value"
	    for value in col.unique():
	        if (not pd.isnull(value)):
	            graph.add_node(column_name + "-" + str(value), type="categorical")
	    

	    counter = 0
	    for cell in col:
	        cell_name = str(column_counter) + "_"+ str(counter)
	        graph.add_node(cell_name, type="cell") # 4. every cell to node, id format: "i_j"
	        # add edge: cell - column
	        graph.add_edge(cell_name, column_name)
	        # add edge: cell - row
	        graph.add_edge(cell_name, "row_"+str(counter))
	        # add edge: cell - categorical value
	        if (not pd.isnull(cell)):
	            categorical_value_name = column_name + "-" + str(cell)
	            if (categorical_value_name not in graph.nodes()):
	                print ("warning!!! create edge with non-existing nodes: "+categorical_value_name)
	            graph.add_edge(cell_name, categorical_value_name)
	        
	        counter+=1
	        
	    column_counter+=1

	return graph


def get_list(graph):
	"""
	return a adjacency list, using LINE format: https://github.com/tangjianpku/LINE
	 
	"""
	row_list = []
	delimiter = " "
	for node in graph.nodes(data=True):
	    if (node[1]['type'] != 'cell'):	# every node except "cell" type can be a source node
	    	for neighbor in graph.neighbors(node[0]):
		    	line = node[0] + delimiter + neighbor + delimiter + "1"	# for now, no weight
		        row_list.append(line)

	return row_list

