#!/usr/bin/env python3
from methods.sonarr_api import Sonarr
from pathlib import Path
import json
import logging
import os
import subprocess
import yaml

		
class Shows(object):
	def __init__(self, config: object):
		self.tags = config.sonarr.get_tags()
		self.series = config.sonarr.get_series()
		self.repo = "https://github.com/manami-project/anime-offline-database.git"
		process = subprocess.Popen(["git", "clone", self.repo], stdout=subprocess.PIPE)
		output = process.communicate()[0]
		config.log.info(f"Git clone output:\t{output}")
		self.anidb = json.loads(open(Path(f"/config/anime-offline-database/anime-offline-database-minified.json")).read())["data"]
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
		self.file = yaml.load(open(config_file), Loader=yaml.FullLoader) if os.path.exists(Path(config_file)) else {"tagging": {"drop": [], "replacements": {}}}
		self.log = logging
		self.log.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
		self.sonarr = Sonarr(url=os.environ["SONARR_URL"], apikey=os.environ["SONARR_API"])
		self.shows = Shows(config=self)
		self.parser()

	def parser(self):
		self.shows.tags = self.sonarr.get_tags()
		previous_tags = self.shows.tags
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
			self.write_tags(show)
		self.log.info("Work Complete")

	def write_tags(self, show):
		self.log.info(f"Processing tags for {show.title}")
		show.sonarr = [tvShow for tvShow in self.shows.series if tvShow["title"]==show.title][0]
		add_tags(tags=aggregate_tags(drop_tags=self.shows.drop_tags, input_tags=show.tags), tagmap=self.sonarr.get_tags(), sonarr=self.sonarr)
		self.shows.tags = self.sonarr.get_tags()
		# try:
		# 	self.shows.tags = self.sonarr.get_tags()
		# except:
		# 	self.shows.tags = previous_tags
		[show.tags.remove(i) for i in show.tags if i in self.shows.drop_tags]
		show.tag_ids = unique([i.get("id") for i in self.shows.tags if (i.get("label") in show.tags)])
		show.sonarr.update({"tags": show.tag_ids})
		self.log.info(f"Tagging has started for {show.title}:\t{show.tags}")
		self.log.info(self.sonarr.update_series(series_id=show.id, data=show.sonarr))
		self.log.info(f"Tagging has completed for {show.title}")
		# try:
		# 	self.log.info(f"Tagging has started for {show.title}:\t{show.tags}")
		# 	self.log.debug(self.sonarr.update_series(series_id=show.id, data=show.sonarr))
		# 	self.log.info(f"Tagging has completed for {show.title}")
		# except:
		# 	pass

def cleanup_tags(tag: str, replacements: dict):
	tag = tag.lower()
	if tag.endswith("ss"):
		tag = tag.rstrip(tag[-1])
	for before, after in replacements.items():
		tag = tag.replace(before, after)
	return tag

def aggregate_tags(drop_tags: list, input_tags: list):
	return unique([tag for tags in input_tags for tag in tags if tag not in drop_tags])

def add_tags(tags: list, tagmap: object, sonarr: object):
	for tag in tags:
		for i in tagmap:
			if i["label"] == tag:
				try:
					radarr.add_tag(tag)
					logging.info(f"+ success adding tag {tag}")
					break
				except:
					pass

def unique(tags):
	return sorted(list(set(tags)))


if __name__ == "__main__":
	config = Config()