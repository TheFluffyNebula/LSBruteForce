import concurrent.futures
import json
import tarfile
import time
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from pynput.keyboard import Key, Controller, Listener

class DataDragonCache(dict):
    """
    Create a cache that interfaces with Riot's data dragon.
    
    Methods
    -------
    refresh() -> None
        Refresh the cache based on the latest data uploaded to the data dragon documentation.
    save(filename: str) -> None
        Save the cache to a json file.
    load(filename: str) -> None
        Load the cache from a json file.
    select(*, champion: bool, item: bool, skin: bool, ability: bool, keystone_rune_and_summoner_spell: bool, nonkeystone_rune: bool) -> set
        Get the set of all possible answers given the required named arguments. See the lolsketch website.
    select_all() -> set
        Get the set of all possible answers.
    """

    # docs
    docs = "https://developer.riotgames.com/docs/lol"

    # ddragon
    url = "https://ddragon.leagueoflegends.com/cdn/"
    language = "en_US"
    categories = {"champion", "summoner", "item", "runesReforged"}

    # lolsketch
    options = {"champion", "item", "skin", "ability", "keystone_rune", "nonkeystone_rune", "summoner_spell"}

    def __init__(self) -> None:
        """Create an empty cache. Refresh or load the cache."""
        # create empty lists (includes duplicates)
        for option in self.options:
            self[option] = []

    def refresh(self) -> None:
        """Refresh the cache based on the latest data uploaded to the data dragon documentation."""
        # get latest
        docs_page = BeautifulSoup(requests.get(self.docs).content, features="html.parser")
        for link in docs_page.find_all("a"):
            if "ddragon" in link.get("href", ""):
                tarball = link["href"]
                break

        # ddragon
        ddragon_request = requests.get(tarball)
        with BytesIO(ddragon_request.content) as byte_stream:
            with tarfile.open(fileobj=byte_stream, mode='r') as ddragon_tarball:
                members = ddragon_tarball.getmembers()
        
        # parallelism
        with concurrent.futures.ThreadPoolExecutor() as executor:

            future_to_member = {executor.submit(self._get_json, member): member 
                                                    for member in members
                                                    if (member.name.endswith('.json') 
                                                        and (self.language in member.name) 
                                                        and any(category in member.name for category in self.categories))}
                                                            
            for future in concurrent.futures.as_completed(future_to_member):
                member = future_to_member[future]
                try:
                    json_obj = future.result()
                    self._add(member, json_obj)
                except Exception as exc:
                    print(f"{member} generated an exception: {exc}")

        # fix Gangplank
        if "<rarityLegendary>Fire at Will</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>" in self["item"]:
            self["item"].remove("<rarityLegendary>Fire at Will</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>")
            self["item"].append("Fire at Will")
        if "<rarityLegendary>Death's Daughter</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>" in self["item"]:
            self["item"].remove("<rarityLegendary>Death's Daughter</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>")
            self["item"].append("Death's Daughter")
        if "<rarityLegendary>Raise Morale</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>" in self["item"]:
            self["item"].remove("<rarityLegendary>Raise Morale</rarityLegendary><br><subtitleLeft><silver>500 Silver Serpents</silver></subtitleLeft>")
            self["item"].append("Raise Morale")

    def save(self, filename: str) -> None:
        """Save the cache to a json file."""
        with open(filename, "w") as file:
            json.dump(self, file)

    def load(self, filename: str) -> None:
        """Load the cache from a json file."""
        with open(filename, "r") as file:
            self.update(json.load(file))

    def select(self, *, champion: bool, item: bool, skin: bool, ability: bool, keystone_rune_and_summoner_spell: bool, nonkeystone_rune: bool) -> set:
        """Get the set of all possible answers given the required named arguments. See the lolsketch website."""
        selection = []
        if champion:
            selection += self["champion"]
        if item:
            selection += self["item"]
        if skin:
            selection += self["skin"]
        if ability:
            selection += self["ability"]
        if keystone_rune_and_summoner_spell:
            selection += self["keystone_rune"] + self["summoner_spell"]
        if nonkeystone_rune:
            selection += self["nonkeystone_rune"]
        return set(selection)
    
    def select_all(self) -> set:
        """Get the set of all possible answers."""
        return self.select(champion=True, item=True, skin=True, ability=True, keystone_rune_and_summoner_spell=True, nonkeystone_rune=True)

    def _get_json(self, member: tarfile.TarInfo) -> dict:
        r = requests.get(self.url + member.name)
        return r.json()

    def _add(self, member: tarfile.TarInfo, json_obj: list | dict) -> None:

        if "runesReforged" in member.name:
            for rune_page in json_obj:
                for keystone_rune in rune_page["slots"][0]["runes"]:
                    self["keystone_rune"].append(keystone_rune["name"])
                for nonkeystone_runepage in rune_page["slots"][1:]:
                    for nonkeystone_rune in nonkeystone_runepage["runes"]:
                        self["nonkeystone_rune"].append(nonkeystone_rune["name"])

        elif "summoner" in member.name:
            for summoner_spell in json_obj["data"].values():
                self["summoner_spell"].append(summoner_spell["name"])

        elif "champion/" in member.name:
            data = list(json_obj["data"].values())[0]
            self["champion"].append(data["name"])
            for ability in data["spells"]:
                self["ability"].append(ability["name"])
            for skin in data["skins"]:
                if skin["name"] != "default":
                    self["skin"].append(skin["name"])

        elif "item" in member.name:
            for item in json_obj["data"].values():
                self["item"].append(item["name"])
                
cache = DataDragonCache()
cache.load("cache.json")

champs = cache.select(champion=True, item=False, skin=False, ability=False, keystone_rune_and_summoner_spell=False, nonkeystone_rune=False)

keyboard = Controller()
time.sleep(2)
def print_champ(champ):
    for char in champ:
        keyboard.press(char)
        keyboard.release(char)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    #time.sleep(0.03)
def print_all():
    for x in champs:
        print_champ(x)

#def on_press(key):
    #pass
def on_release(key):
    if key == Key.esc:
        t1 = time.time()
        print_all()
        t2 = time.time()
        print(t2-t1)
        return False
with Listener(
        #on_press=on_press,
        on_release=on_release) as listener:
    listener.join()