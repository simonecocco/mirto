from numpy import array as numpy_array, zeros as numpy_zeros, uint16
from dpkt.pcap import Reader as PCAPReader
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import Birch
from os.path import exists, isfile

class Fingerprinter:
    def __init__(self, logger, process_lock=None, packet_dict=None, user_num=21, num_pkt_for_train=8000, training_pcap_file=None, n_components=3):
        self.user_num = user_num
        self.main_logger = logger
        self.main_process_lock = process_lock
        self.truncated_svd = TruncatedSVD(n_components=n_components)
        self.birch = Birch(n_clusters=n_clusters)
        self.trained: bool = False
        self.labels = {i:f'user{i}' for i in range(user_num)}
        if training_pcap_file is not None and exists(training_pcap_file) and isfile(training_pcap_file):
            self.main_logger.info(f'using {training_pcap_file} to train and using max {num_pcap_for_train} packets')
            self.trained = self._pcap_read(pcap_file)

    def _pcap_read(self, pcap_file, max_pkts=8000) -> bool:
        try:
            pkts_list = []
            with open(pcap_file, 'rb') as pcap:
                pcap_reader = PCAPReader(pcap)
                count = 0
                for timestamp, buf in pcap_reader:
                    if count == max_pkts:
                        break
                    a = self._convert_to_feature_vector(buf)
                    pkts_list.append(a)
                    count += 1
            pkts_list = numpy_array(pkts_list, dtype=uint16)
            self.train(pkts_list)
            self.main_logger.info(f'train complete')
        except:
            self.main_logger.info(f'exception using pcap file. using collection to train')
            return False

    def train(self, pkts_list):
        truncated_data = self.truncated_svd.fit_transform(pkts_list)
        self.birch.fit(truncated_data)

    def _convert_to_feature_vector(self, seqs, max_val=255):
        zero_arr = numpy_zeros(max_val+1)
        for val in seq:
            zero_arr[val] += 1
        return numpy_array([zero_arr], dtype=uint16)

    def predict(self, b):
        feature_vec = self._convert_to_feature_vector(b)
        reduced_data = self.truncated_svd.transform(feature_vec)
        return self.birch.predict(reduce_data)

    def set_label_for_cluster_n(self, cluster_n, label):
        self.labels[cluster_n] = label

    def get_label_for_cluster_n(self, cluster_n):
        return self.labels.get(cluster_n, 0)