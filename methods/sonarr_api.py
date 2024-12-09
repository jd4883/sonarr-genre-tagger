from pyarr.sonarr import SonarrAPI
import time
import json
import requests


class Sonarr(object):
	def __init__(self, url: str, apikey: str):
		self.api = SonarrAPI(host_url = url.replace("/api/v3", ""), api_key = apikey)
		self.api_key = apikey
		self.host_url = url
		self.api_suffix = "api/v3"

	def sonarr_api_request(self, url, request_type = "get", data = dict()):
		backoff_timer = 2
		payload = json.dumps(data)
		request_payload = dict()
		headers = {
			'X-Api-Key': self.api_key,
	        "Content-Type": "application/json",
	        "accept": "application/json",
		}
		if request_type not in ["post", "put", "delete"]:
			request_payload = requests.get(url, headers = headers, data = payload)
		elif request_type == "put":
			request_payload = requests.put(url, headers = headers, data = payload)
		elif request_type == "post":
			request_payload = requests.post(url, headers = headers, data = payload)
		elif request_type == "delete":
			request_payload = requests.delete(url, headers = headers, data = payload)
		time.sleep(backoff_timer)
		return request_payload.json()

	def update_series(self, series_id, data: dict):
		return self.api.upd_series(data)
	
	def add_tag(self, tag: str):
		return self.api.create_tag(label=tag)

	def get_series(self):
		# return self.sonarr_api_request(f"{self.host_url}/{self.api_suffix}/series")
		return self.api.get_series()

	def get_tags(self):
		# return self.sonarr_api_request(f"{self.host_url}/{self.api_suffix}/tag")
		return self.api.get_tag()