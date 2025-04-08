import numpy as np
from sklearn.utils.extmath import row_norms, squared_norm
from sklearn.cluster import KMeans

class DynamicByteClusterer:
    def __init__(self, n_clusters=8, batch_size=100, feature_weighting=True, max_iter=100, tol=1e-4):
        self.n_clusters = n_clusters
        self.batch_size = batch_size
        self.feature_weighting = feature_weighting
        self.max_iter = max_iter
        self.tol = tol
        self.centroids = None
        self.feature_weights = np.ones((256,))
        self.converged = False

    def _weighted_distance(self, X, centroid):
        return np.sum(np.abs(X - centroid) * self.feature_weights, axis=1)

    def _init_centroids(self, X):
        # Utilizza K-Means++ per l'inizializzazione dei centroidi
        n_samples, n_features = X.shape
        centers = np.empty((self.n_clusters, n_features), dtype=X.dtype)
        center_id = np.random.randint(n_samples)
        centers[0] = X[center_id]
        closest_dist_sq = self._weighted_distance(X, centers[0]) ** 2
        current_pot = closest_dist_sq.sum()
        for c in range(1, self.n_clusters):
            rand_vals = np.random.random_sample() * current_pot
            candidate_ids = np.searchsorted(np.cumsum(closest_dist_sq), rand_vals)
            centers[c] = X[candidate_ids]
            dist_sq = self._weighted_distance(X, centers[c]) ** 2
            closest_dist_sq = np.minimum(closest_dist_sq, dist_sq)
            current_pot = closest_dist_sq.sum()
        self.centroids = centers

    def partial_fit(self, X):
        if self.centroids is None:
            self._init_centroids(X)

        distances = np.array([self._weighted_distance(X, centroid) for centroid in self.centroids]).T
        labels = np.argmin(distances, axis=1)

        new_centroids = np.array([X[labels == i].mean(axis=0) if np.any(labels == i) else self.centroids[i] for i in range(self.n_clusters)])

        # Verifica la convergenza
        if self.centroids is not None:
            centroid_diff = np.sum((new_centroids - self.centroids) ** 2)
            if centroid_diff < self.tol:
                self.converged = True

        self.centroids = new_centroids

        if self.feature_weighting:
            variances = np.array([np.var(X[labels == i], axis=0) if np.any(labels == i) else np.zeros(X.shape[1]) for i in range(self.n_clusters)])
            avg_variance = np.mean(variances, axis=0)
            self.feature_weights = 1 / (avg_variance + 1e-6)

        return labels

    def fit_predict(self, X):
        num_samples = X.shape[0]
        labels = np.zeros((num_samples,))
        for i in range(0, num_samples, self.batch_size):
            batch = X[i:i + self.batch_size]
            labels[i:i + self.batch_size] = self.partial_fit(batch)
            if self.converged:
                break
        return labels

    def predict(self, X):
        if self.centroids is None:
            raise ValueError("Il modello non è stato addestrato. Utilizzare fit_predict o partial_fit prima di predict.")
        
        num_samples = X.shape[0]
        labels = np.zeros((num_samples,))
        for i in range(0, num_samples, self.batch_size):
            batch = X[i:i + self.batch_size]
            distances = np.array([self._weighted_distance(batch, centroid) for centroid in self.centroids]).T
            labels[i:i + self.batch_size] = np.argmin(distances, axis=1)
        return labels

def create_feature_vectors(sequences, max_byte=255, normalize=False, dtype=np.uint16):
    """
    Crea vettori di feature a partire da sequenze di byte.

    Parametri:
    sequences (list di liste di int): Le sequenze di byte da convertire in vettori di feature.
    max_byte (int): Il valore massimo dei byte. Default: 255.
    normalize (bool): Se True, normalizza i vettori di feature dividendo per la lunghezza della sequenza. Default: False.
    dtype (tipo di dati NumPy): Il tipo di dati da utilizzare per i vettori di feature. Default: np.uint16.

    Ritorna:
    np.ndarray: I vettori di feature.
    """
    feature_vectors = np.zeros((len(sequences), max_byte + 1), dtype=dtype)
    for i, seq in enumerate(sequences):
        np.add.at(feature_vectors[i], seq, 1)
    if normalize:
        lengths = np.array([len(seq) for seq in sequences])
        feature_vectors = feature_vectors / lengths[:, np.newaxis]
    return feature_vectors

