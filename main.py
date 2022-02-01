#!/usr/bin/env python3
from methods.sonarr_api import SonarrAPI
import json
from pathlib import Path
import logging
import yaml
import os
import git


class Shows(object):
    def __init__(self, sonarr: object, config: dict):
        self.tags = sonarr.get_tags()
        self.series = sonarr.get_series()
        self.gitbase = "/config/anime-offline-database"
        logging.debug(f"Git pull output:\t{git.cmd.Git(self.gitbase).pull()}")
        self.anidb = json.loads(open(Path(f"{self.gitbase}/anime-offline-database-minified.json")).read())["data"]
        self.aggregate = list()
        self.drop_tags = config["tagging"].get("drop", [])
        self.replacement_tags = config["tagging"].get("replacements", {}).update({" ": "_"})

class Show(object):
    def __init__(self, show: dict):
        self.title = show.get("title")
        self.tags = show.get("genres", [])
        self.tag_ids = show.get("tags", [])
        self.id = show.get("id")
        self.sonarr = dict()
        self.type = show.get("seriesType")

def set_logging():
    logfile = 'anime-tagging.log'
    if os.path.exists(logfile):
        os.remove(logfile)
    logging.basicConfig(filename=logfile, level=logging.INFO)

def cleanup_tags(tag: str, replacements: dict):
    tag = tag.lower()
    if tag.endswith("ss"):
        tag = tag.rstrip(tag[-1])
    for before, after in replacements.items():
        tag = tag.replace(before, after)
    return tag

def aggregate_tags(drop_tags: list, input_tags: list):
    all_tags = list()
    for tags in input_tags:
        for tag in tags:
            if tag not in all_tags:
                all_tags.append(tag)
    [all_tags.remove(i) for i in all_tags if i in drop_tags]
    return sorted(list(set(all_tags)))

def add_tags(tags: list, tagmap: object):
    for tag in tags:
        for i in tagmap:
            try:
                if i.label == tag:
                    sonarr.add_tag(tag)
                    logging.info(f"+ success adding tag {tag}")
                    break
            except:
                pass



def write_tags(shows: object, sonarr: object):
    shows.tags = sonarr.get_tags()
    previous_tags = shows.tags
    shows.tags = aggregate_tags(drop_tags=shows.drop_tags, input_tags=[show.tags for show in shows.aggregate])
    for show in shows.aggregate:
        logging.info(f"Processing tags for {show.title}")
        show.sonarr = [tvShow for tvShow in shows.series if tvShow["title"]==show.title][0]
        add_tags(tags=aggregate_tags(drop_tags=shows.drop_tags, input_tags=show.tags), tagmap=sonarr.get_tags())
        try:
            shows.tags = sonarr.get_tags()
        except:
            shows.tags = previous_tags
        show.tag_ids = sorted([i.get("id") for i in shows.tags if (i.get("label") in show.tags)])
        show.sonarr.update({"tags": show.tag_ids})
        try:
            print(f"Tagging has started for {show.title}:\t{show.tags}")
            logging.info(f"Tagging has started for {show.title}:\t{show.tags}")
            sonarr.update_series(series_id=show.id, data=show.sonarr)
            logging.info(f"Tagging has completed for {show.title}")
        except:
            pass



if __name__ == "__main__":
    set_logging()
    config = yaml.load(open("config.yaml"), Loader=yaml.FullLoader) if os.path.exists(Path("config.yaml")) else dict()
    sonarr = SonarrAPI(url=os.environ["SONARR_URL"], apikey=os.environ["SONARR_API"])
    shows = Shows(sonarr=sonarr, config=config)
    for s in shows.series:
        show = Show(s)
        if show.type == "anime":
            show.tags += ["anime", "animated", "animation", "japanese"]
            for anime in shows.anidb:
                if anime["title"] == show.title:
                    show.tags += anime["tags"]
                    break
        show.tags = [cleanup_tags(tag=i, replacements=shows.replacement_tags) for i in sorted(list(set(show.tags)))]
        shows.aggregate.append(show)
    write_tags(shows=shows, sonarr=sonarr)
