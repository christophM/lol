import sys
sys.path.append("../lib")
import rawpi
import json
import os
import urllib


BASE_URI = "http://ddragon.leagueoflegends.com/cdn/5.2.1/img/"

# use script like this: python download_images.py ../projects/winprob/app/static/

def download_images(target_folder, entity, image_data):
    ## mkdir for images in static folder
    os.mkdir(target_folder + entity + "/")
    ## Iterate through image uris
    for key, image in image_data.iteritems():
        ## Download image per champion
        urllib.urlretrieve("%s/%s/%s.png" % (BASE_URI, entity, key), 
                           "%s/%s/%s.png" % (target_folder, entity, image["id"]))
        


def main():
    target_folder = sys.argv[1]
    os.mkdir(target_folder)
    print target_folder
    ## champions
    try: 
        champions = json.loads(rawpi.get_champion_list("na", champData="image").text)["data"]
        spells = json.loads(rawpi.get_spell_list("na", spellData="image").text)["data"]
        items = json.loads(rawpi.get_item_list("na", itemListData="image").text)["data"]
    except:
        print "Could not reach Riot API"
    download_images(target_folder, "champion", champions)
    download_images(target_folder, "spell", spells)
    download_images(target_folder, "item", items)




if __name__ =="__main__":
    main()

