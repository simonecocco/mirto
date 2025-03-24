import time
import dpkt
from argparse import ArgumentParser
from numpy import array, zeros
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import Birch
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt 

def read_pkts(filename='test.pcap', verbose=True):
    pkts = []
    pkts_copy = []
    with open('test.pcap', 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        for timestamp, buf in pcap:
            a = [b for b in buf]
            pkts.append(a)
            pkts_copy.append(a.copy())

    if verbose: print(f'Readed {len(pkts)} pkts') 
    return pkts, pkts_copy

def reduce_data(data, n_components=2):
    svd = TruncatedSVD(n_components=n_components)
    new_data = svd.fit_transform(data)
    return new_data, svd

def compute_clusters(data, n_clusters=21):
    birch = Birch(n_clusters=n_clusters)
    clusters = birch.fit_predict(data)
    return clusters, birch

def create_feature_vectors(sequences, max_byte=255):
    feature_vectors = []
    for seq in sequences:
        counts = zeros(max_byte + 1)
        for byte in seq:
            counts[byte] += 1
        feature_vectors.append(counts)
    return array(feature_vectors)

def evaluate(data, clusters):
    silhouette_avg = silhouette_score(data, clusters)
    print(f"Silhouette Score: {silhouette_avg}")

def print_graph(data, clusters):
    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(data)
    plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=clusters)
    plt.title('t-SNE visualization of clusters')
    plt.show()

def assign_labels(label_dict, clusters):
    assigned_labels = [label_dict[cluster] for cluster in clusters]
    return assigned_labels

def main(args):
    start_time = time.time()
    
    packets, packets_copy = read_pkts(args.f)
    vector = create_feature_vectors(packets)
    data_reduced, svd = reduce_data(vector, args.components_n)
    clusters, birch = compute_clusters(data_reduced, args.clusters_n)
    evaluate(data_reduced, clusters)
    assigned_labels = assign_labels({i: f'user{i+1}' for i in range(args.clusters_n)}, clusters)
    #print(assigned_labels)

    end_time = time.time()

    print_graph(data_reduced, clusters)

    print(f'tempo totale: {end_time-start_time} secondi')

if __name__ == '__main__':
    aparse = ArgumentParser()
    aparse.add_argument('--clusters-n', type=int, default=21)
    aparse.add_argument('--components-n', type=int, default=2)
    aparse.add_argument('-f', type=str, default='test.pcap')
    args = aparse.parse_args()

    main(args)
