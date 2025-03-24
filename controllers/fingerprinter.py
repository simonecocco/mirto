from numpy import array as numpy_array, zeros as numpy_zeros
from dpkt import pcap
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import 

class Fingerprinter:
    def __init__(self, process_lock=None, packet_dict=None, user_num=21, num_pcap_for_train=8000, training_pcap_file=None, n_components=3):
        self.user_num = user_num

    def _convert_to_feature_vector(self, seqs, max_val=255):
        zero_arr = numpy_zeros(max_val+1)
        for val in seq:
            zero_arr[val] += 1
        return numpy_array([zero_arr])

    def predict(self, b):
        feature_vec = self._convert_to_feature_vector(b)

    def set_label_for_cluster_n(self, cluster_n, label):
        pass

    def get_label_for_cluster_n(self, cluster_n):
        pass