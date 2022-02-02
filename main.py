#!/usr/bin/env python3
from methods.sonarr_api import SonarrAPI
from pathlib import Path
import os

class Shows(object):
    def __init__(self, config: object):
        import json
        import git
        self.tags = config.sonarr.get_tags()
        self.series = config.sonarr.get_series()
        self.gitbase = "/config/anime-offline-database"
        config.log.info(f"Git pull output:\t{git.cmd.Git(self.gitbase).pull()}")
        self.anidb = json.loads(open(Path(f"{self.gitbase}/anime-offline-database-minified.json")).read())["data"]
        self.aggregate = list()
        self.drop_tags = config.file["tagging"].get("drop", [])
        self.replacement_tags = config.file["tagging"].get("replacements", {})
        self.replacement_tags[" "] = "_" # this doesnt translate nice from a configmap so I injected it; besides tags don't accept spacing in sonarr

class Show(object):
    def __init__(self, show: dict):
        self.title = show.get("title")
        self.tags = unique(show.get("genres", []))
        self.tag_ids = unique(show.get("tags", []))
        self.id = show.get("id")
        self.sonarr = dict()
        self.type = show.get("seriesType")

class Config:
    def __init__(self, config_file="/config/config.yaml"):
        import yaml
        import logging
        self.file = yaml.load(open(config_file), Loader=yaml.FullLoader) if os.path.exists(Path(config_file)) else {"tagging": {"drop": [], "replacements": {}}}
        self.log = logging
        self.log.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        self.sonarr = SonarrAPI(url=os.environ["SONARR_URL"], apikey=os.environ["SONARR_API"])
        self.shows = Shows(config=self)
        self.parser()

    def parser(self):
        for s in self.shows.series:
            show = Show(s)
            if show.type == "anime":
                show.tags += ["anime", "animated", "animation", "japanese"]
                for anime in self.shows.anidb:
                    if anime["title"] == show.title:
                        show.tags += anime["tags"]
                        break
            show.tags = unique([cleanup_tags(tag=i, replacements=self.shows.replacement_tags) for i in sorted(list(set(show.tags)))])
            self.shows.aggregate.append(show)
        self.write_tags()

    def write_tags(self):
        self.shows.tags = self.sonarr.get_tags()
        previous_tags = self.shows.tags
        self.shows.tags = aggregate_tags(drop_tags=self.shows.drop_tags, input_tags=[show.tags for show in self.shows.aggregate])
        for show in self.shows.aggregate:
            self.log.info(f"Processing tags for {show.title}")
            show.sonarr = [tvShow for tvShow in self.shows.series if tvShow["title"]==show.title][0]
            add_tags(tags=aggregate_tags(drop_tags=self.shows.drop_tags, input_tags=show.tags), tagmap=self.sonarr.get_tags(), sonarr=self.sonarr)
            try:
                self.shows.tags = self.sonarr.get_tags()
            except:
                self.shows.tags = previous_tags
            [show.tags.remove(i) for i in show.tags if i in self.shows.drop_tags]
            show.tag_ids = unique([i.get("id") for i in self.shows.tags if (i.get("label") in show.tags)])
            show.sonarr.update({"tags": show.tag_ids})
            try:
                self.log.info(f"Tagging has started for {show.title}:\t{show.tags}")
                self.sonarr.update_series(series_id=show.id, data=show.sonarr)
                self.log.info(f"Tagging has completed for {show.title}")
            except:
                pass

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
    return unique(all_tags)

def add_tags(tags: list, tagmap: object, sonarr: object):
    for tag in tags:
        for i in tagmap:
            try:
                if i.label == tag:
                    sonarr.add_tag(tag)
                    logging.info(f"+ success adding tag {tag}")
                    break
            except:
                pass

def unique(tags):
    return sorted(list(set(tags)))


if __name__ == "__main__":
    config = Config()