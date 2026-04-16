async function runClustering() {
    const method = document.getElementById('method').value;
    const clusters = document.getElementById('clusters').value;

    const response = await fetch('/cluster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ method, clusters })
    });

    const data = await response.json();
    renderPlots(data);
}

function renderPlots(data) {
    // 1. Dendrogram
    const dendroTraces = [];
    for (let i = 0; i < data.dendrogram.icoord.length; i++) {
        dendroTraces.push({
            x: data.dendrogram.icoord[i],
            y: data.dendrogram.dcoord[i],
            type: 'scatter', mode: 'lines',
            line: { color: 'rgb(50,50,50)' },
            showlegend: false
        });
    }
    Plotly.newPlot('dendro-plot', dendroTraces, { title: 'Tree Hierarchy' });

    // 2. PCA Scatter
    const pcaTrace = {
        x: data.pca.x,
        y: data.pca.y,
        mode: 'markers',
        type: 'scatter',
        text: data.pca.ids,
        marker: { 
            color: data.pca.clusters, 
            colorscale: 'Viridis',
            size: 6,
            opacity: 0.7
        }
    };
    Plotly.newPlot('pca-plot', [pcaTrace], { 
        title: 'Genes in PCA Space (Colored by Cluster)',
        xaxis: { title: 'PC1' }, yaxis: { title: 'PC2' }
    });

    // 3. Profiles
    const profileTraces = data.profiles.map(p => ({
        x: data.time_points,
        y: p.profile,
        type: 'scatter',
        mode: 'lines+markers',
        name: `Cluster ${p.cluster} (n=${p.count})`
    }));
    Plotly.newPlot('profile-plot', profileTraces, { 
        title: 'Expression Over Time',
        xaxis: { title: 'Time' }, yaxis: { title: 'Standardized Expression' }
    });
}

// Initial Run
window.onload = runClustering;