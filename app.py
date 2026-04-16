from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json

app = Flask(__name__)

# Load and prepare data globally (or load per request)
DATA_FILE = 'Spellman.csv'

def load_data():
    df = pd.read_csv(DATA_FILE)
    gene_ids = df.iloc[:, 0].tolist()
    time_points = df.columns[1:].tolist()
    data = df.iloc[:, 1:].values
    # Fill any NaNs if they existed
    data = np.nan_to_num(data)
    # Standardize data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    return df, gene_ids, time_points, data_scaled

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cluster', methods=['POST'])
def cluster():
    params = request.get_json()
    linkage_method = params.get('method', 'ward')
    metric = params.get('metric', 'euclidean')
    n_clusters = int(params.get('clusters', 5))
    
    df, gene_ids, time_points, data_scaled = load_data()
    
    # Perform Hierarchical Clustering
    Z = linkage(data_scaled, method=linkage_method, metric=metric)
    
    # Get cluster assignments
    clusters = fcluster(Z, n_clusters, criterion='maxclust')
    
    # Prepare Dendrogram Data (Truncated for performance)
    dendro = dendrogram(Z, truncate_mode='lastp', p=30, no_plot=True)
    
    # PCA for 2D Visualization
    pca = PCA(n_components=2)
    pca_results = pca.fit_transform(data_scaled)
    
    # Average expression profile per cluster
    cluster_profiles = []
    for i in range(1, n_clusters + 1):
        idx = (clusters == i)
        avg_profile = np.mean(data_scaled[idx], axis=0).tolist()
        cluster_profiles.append({
            'cluster': i,
            'count': int(np.sum(idx)),
            'profile': avg_profile
        })

    # Sample Heatmap data (taking a subset or sorted)
    # To keep it interactive, we provide a subset or the cluster averages
    
    response = {
        'dendrogram': {
            'icoord': dendro['icoord'],
            'dcoord': dendro['dcoord'],
            'leaves': dendro['leaves']
        },
        'pca': {
            'x': pca_results[:, 0].tolist(),
            'y': pca_results[:, 1].tolist(),
            'clusters': clusters.tolist(),
            'ids': gene_ids
        },
        'profiles': cluster_profiles,
        'time_points': time_points
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)