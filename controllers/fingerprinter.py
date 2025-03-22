import numpy as np
import random

class IncrementalKMeans:
    def __init__(self, num_clusters=21, max_distance=None):
        self.num_clusters = num_clusters
        self.max_distance = max_distance  # Limite di distanza per l'inizializzazione
        self.centroids = []
        self.cluster_sizes = []

    def _update_centroid(self, cluster_id, new_point):
        """
        Aggiorna il centroid del cluster specificato con il nuovo dato.
        """
        if isinstance(new_point, list):
            new_point = np.array(new_point)
        self.cluster_sizes[cluster_id] += 1
        decay_factor = 1.0 / self.cluster_sizes[cluster_id]
        self.centroids[cluster_id] = (
            self.centroids[cluster_id] * (1 - decay_factor) +
            new_point * decay_factor
        )

    def assign_cluster(self, new_point):
        """
        Assegna il nuovo dato al cluster più vicino o inizializza un nuovo cluster se necessario.
        """
        if isinstance(new_point, list):
            new_point = np.array(new_point)
        
        if len(self.centroids) < self.num_clusters:
            if self._initialize_cluster(new_point):
                return len(self.centroids) - 1
            else:
                return self._assign_to_closest(new_point)
        else:
            return self._assign_to_closest(new_point)

    def _initialize_cluster(self, new_point):
        """
        Inizializza un nuovo cluster con il nuovo dato se non sono presenti altri cluster inizializzati.
        """
        if len(self.centroids) < self.num_clusters:
            if isinstance(new_point, list):
                new_point = np.array(new_point)
            self.centroids.append(new_point.copy())
            self.cluster_sizes.append(1)
            return True
        return False

    def _assign_to_closest(self, new_point):
        """
        Assegna il nuovo dato al cluster più vicino e aggiorna il centroid.
        """
        if isinstance(new_point, list):
            new_point = np.array(new_point)
        distances = np.array([np.linalg.norm(new_point - centroid) for centroid in self.centroids])
        closest_cluster = np.argmin(distances)
        if self.max_distance is not None and distances[closest_cluster] > self.max_distance:
            if len(self.centroids) < self.num_clusters:
                # Inizializza un nuovo cluster
                self._initialize_cluster(new_point)
                return len(self.centroids) - 1
            else:
                # Assegna comunque al cluster più vicino
                pass
        self._update_centroid(closest_cluster, new_point)
        return closest_cluster

    def set_max_distance(self, max_distance):
        """
        Imposta il limite di distanza per l'inizializzazione di nuovi cluster.
        """
        self.max_distance = max_distance

'''
# Esempio di utilizzo
incremental_kmeans = IncrementalKMeans(num_clusters=21, max_distance=2.0)

# Simulazione di nuovi dati come una lista di liste di interi
data_points = []
for _ in range(100 + 200):
    new_point = [random.randint(0, 10) for _ in range(3)]  # Esempio: 3 dimensioni, valori interi tra 0 e 10
    data_points.append(new_point)

for new_point in data_points[:100]:
    cluster_id = incremental_kmeans.assign_cluster(new_point)
    print(f"Il dato {new_point} è stato assegnato al cluster #{cluster_id}")

for new_point in data_points[100:]:
    cluster_id = incremental_kmeans.assign_cluster(new_point)
    print(f"Il dato {new_point} è stato assegnato al cluster #{cluster_id}")

print("\nInformazioni finali sugli cluster:")
for i, centroid in enumerate(incremental_kmeans.centroids):
    print(f"Cluster {i}: centroid={centroid}, dimensione={incremental_kmeans.cluster_sizes[i]}")'
'''