import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class ChampionCluster:
    def __init__(self, df):
        self.df = df
        # Key combat stats
        self.features = [
            'hp', 'hpperlevel', 'movespeed', 'armor', 
            'spellblock', 'attackrange', 'hpregen', 
            'attackdamage', 'attackspeed'
        ]

    def process(self, n_clusters=5):
        """
        Execute the complete pipeline: Clean -> Scale -> K-Means -> PCA
        """
        # 1. Prepare data (fill nulls with 0 for security)
        data_for_ml = self.df[self.features].fillna(0)

        # 2. Scale data (REQUIRED for PCA and K-Means)
        # This puts all stats on the same scale (mean 0, variance 1)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_for_ml)

        # 3. Apply K-Means (Find groups)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.df['cluster_label'] = kmeans.fit_predict(scaled_data)
        self._name_clusters()

        # 4. Apply PCA (Reduce to 2 dimensions for visualization)
        pca = PCA(n_components=2)
        pca_components = pca.fit_transform(scaled_data)

        # Save abstract coordinates
        self.df['pca_x'] = pca_components[:, 0]
        self.df['pca_y'] = pca_components[:, 1]
        
        return self.df

    def _name_clusters(self):
        """
        Analyze the averages of each cluster to give it an RPG name.
        """
        # Calculate the average of each stat by cluster
        means = self.df.groupby('cluster_label')[self.features].mean()
        
        # Dictionary to save the names: {0: "Name", 1: "Other"...}
        names_map = {}
        
        # --- Rule 1: THE TANK ---
        # The cluster with the highest average Armor
        tank_id = means['armor'].idxmax()
        names_map[tank_id] = "Vanguards (Tanks)"
        
        # --- Rule 2: THE ADC (Tirador) ---
        # The cluster with the highest average Attack Range
        # (Exclude the tank in case it coincides)
        remaining = means.drop([tank_id], errors='ignore')
        if not remaining.empty:
            adc_id = remaining['attackrange'].idxmax()
            names_map[adc_id] = "Marksmen"
        
        # --- Rule 3: THE ASSASSIN/MOBILE ---
        # Of the remaining, the one with the highest Movement Speed or Damage
        remaining = remaining.drop([adc_id], errors='ignore')
        if not remaining.empty:
            speed_id = remaining['movespeed'].idxmax()
            names_map[speed_id] = "Skirmishers"

        # --- Rule 4: THE MAGES/SUPPORTS (Papel) ---
        # Of the remaining, the one with the LEAST base health
        remaining = remaining.drop([speed_id], errors='ignore')
        if not remaining.empty:
            glass_cannon_id = remaining['hp'].idxmin()
            names_map[glass_cannon_id] = "Mages/Artillery"

        # --- Rule 5: WHAT REMAINS ---
        # Normally are the balanced Fighters
        for i in means.index:
            if i not in names_map:
                names_map[i] = "Fighters"

        # Apply the mapping to the DataFrame
        self.df['cluster_name'] = self.df['cluster_label'].map(names_map)