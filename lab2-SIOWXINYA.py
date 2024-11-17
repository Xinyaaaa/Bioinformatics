import streamlit as st    
import requests
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

#Task 2(a)
def retrieve_ppi_biogrid(target_protein):
    biogrid_url = "https://webservice.thebiogrid.org/interactions"
    params = {
        "accessKey":"17d5fe5963e2c014eef448e3e1e53864",
        "format":"json",
        "searchNames": True,
        "geneList":target_protein,
        "organism":"9606",
        "searchbiogridids":True,
        "includeInteractors":True
    }
    response = requests.get(biogrid_url, params=params)
    network  = response.json() 
    network_df = pd.DataFrame.from_dict(network, orient='index')
    return network_df

#Task 2(b)
def retrieve_ppi_string(target_protein):
    string_url = "https://string-db.org/api/json/network"
    params = {
        "identifiers":target_protein,
        "species":"9606"
    }
    response = requests.get(string_url, params=params)
    network  = response.json()
    network_df = pd.json_normalize(network)
    return network_df

#Task 3(a)
def generate_network(dataframe):
    if 'OFFICIAL_SYMBOL_A' in dataframe.columns and 'OFFICIAL_SYMBOL_B' in dataframe.columns:
        network_graph = nx.from_pandas_edgelist(dataframe, "OFFICIAL_SYMBOL_A", "OFFICIAL_SYMBOL_B")
    elif 'preferredName_A' in dataframe.columns and 'preferredName_B' in dataframe.columns:
        network_graph = nx.from_pandas_edgelist(dataframe, "preferredName_A", "preferredName_B")
    else:
        st.error("Error !")
        return None, {}

    graph_details = {
        "Number of edges": network_graph.number_of_edges(),
        "Number of nodes": network_graph.number_of_nodes()
    }

    return network_graph, graph_details

#Task 4(a)
def get_centralities(network_graph):
    centralities = {
        "Degree Centrality": nx.degree_centrality(network_graph),
        "Betweenness Centrality": nx.betweenness_centrality(network_graph),
        "Closeness Centrality": nx.closeness_centrality(network_graph),
        "Eigenvector Centrality": nx.eigenvector_centrality(network_graph, max_iter=1000),
        "PageRank Centrality": nx.pagerank(network_graph)
    }
    
    return centralities

#Task 5
st.title('Lab 2 - SIOW XIN YA')

protein_id = st.text_input('Enter Protein ID')
selected = st.selectbox('Choose a database',['BioGRID','STRING'],index =None, placeholder='select a database')
retrieve = st.button('Retrieve')

if retrieve:
    if protein_id!="":
    	
        col1,col2 = st.columns(2)

        with col1:
            st.subheader('PPI data information')
            
            if selected=='BioGRID':
                ppi_data=retrieve_ppi_biogrid(protein_id)
            else:
                ppi_data=retrieve_ppi_string(protein_id)
            
            st.write("PPI Data")
            st.dataframe(ppi_data)

            network_graph, graph_details = generate_network(ppi_data)

            if network_graph:
                st.write("Details of Data")
                st.write(graph_details)

                st.write("Visualization of Network")
                slayout = nx.spring_layout(network_graph, seed=123)
                nx.draw(network_graph, slayout, with_labels=True, node_size=1000, node_color='lightblue', font_size=8)
                st.pyplot(plt) # Display the plot in Streamlit
                plt.clf()

        with col2:
            st.subheader('Centrality Measures')
            if network_graph:
                centralities = get_centralities(network_graph)
                
                tab1, tab2 = st.tabs(["Centralities","Top 5 Analysis"])

                with tab1:
                    for name, values in centralities.items():
                        st.write(f"{name:}")
                        st.json(values)

                with tab2:
                    for name, centrality in centralities.items():
                        st.write(f"Top 5 {name}:")
                        sorted_centrality = sorted(centrality.items(), key=lambda x:-x[1])[:5]
                        st.json(sorted_centrality)

else:
    st.warning('Please enter Protein ID')