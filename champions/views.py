from django.shortcuts import render
from champions.logics.data_fetcher import LeagueDataFetcher
from champions.logics.ml_engine import ChampionCluster
from django.http import JsonResponse

def champion_list(request):
    try:
        fetcher = LeagueDataFetcher()
        champions_df = fetcher.get_champions_data()

        ml_engine = ChampionCluster(champions_df)
        champions_df_enriched = ml_engine.process(n_clusters=5)
        
        data = champions_df_enriched.to_dict('records')
        
        return JsonResponse({
            'status': 'success',
            'count': len(data),
            'data': data,
            }, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error',
        'message': str(e)
        }, status=500)

# Create your views here.
