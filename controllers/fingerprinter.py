from numpy import array as numpy_array, zeros as numpy_zeros, ubyte
from dpkt.pcap import Reader as PCAPReader
from utils.const import *
from controllers.clustering_alg import *

class Fingerprinter:
    def __init__(self, logger, process_lock=None, shared_dict=None, cluster_n=3, num_pkt_for_train=1000, n_components=5):
        self.cluster_n = cluster_n
        self.main_logger = logger
        self.main_process_lock = process_lock
        self.main_shared_dict = shared_dict
        self.num_pkt_for_train = num_pkt_for_train
        self.labels = self.main_shared_dict[FINGERPRINTER_LABELS_KEY]
        self.clustering_alg = DynamicByteClusterer(n_clusters=cluster_n, batch_size=1)

    def predict(self, b):
        data = create_feature_vectors([b])
        self.clustering_alg.partial_fit(data)
        return self.get_label_for_cluster_n(int(self.clustering_alg.predict(data)))

    def set_label_for_cluster_n(self, cluster_n, label):
        self.labels[cluster_n] = label

    def get_label_for_cluster_n(self, cluster_n):
        return self.labels.get(cluster_n, 'UNK')