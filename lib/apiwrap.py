import rawpi
import json



def get_champion_map(region="na"):
    champs = json.loads(rawpi.get_champion_list(region).text)["data"]
    return dict([(v["id"], k) for k,v in champs.iteritems()])
