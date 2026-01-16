import requests
import pandas as pd
from django.conf import settings

class LeagueDataFetcher:
    def __init__(self):
        self.api_key = settings.RIOT_API_KEY
        self.version = self._get_latest_version()

    def _get_latest_version(self):
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(url)
        return response.json()[0]

    def get_champions_data(self):
        url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/data/es_MX/champion.json"
        response = requests.get(url)
        response.raise_for_status()

        data_json = response.json()
        champions_data = data_json['data']

        processed_list = []
        for champion_id, champion_data in champions_data.items():
            stats = champion_data['stats'].copy()
            stats['id'] = champion_id
            stats['name'] = champion_data['name']
            stats['title'] = champion_data['title']
            stats['blurb'] = champion_data['blurb']
            stats['image'] = champion_data['image']['full']
            processed_list.append(stats)
            
        processed_df = pd.DataFrame(processed_list)
        return processed_df