from pyarr.sonarr import SonarrAPI
# import time
# import json
# import requests


class Sonarr(object):
	def __init__(self, url: str, apikey: str):
		self.api = RadarrAPI(host_url = url.replace("/api/v3", ""), api_key = apikey)

	# def sonarr_api_request(self, url, request_type = "get", data = dict()):
	# 	backoff_timer = 2
	# 	payload = json.dumps(data)
	# 	request_payload = dict()
	# 	headers = {
	# 		'X-Api-Key': self.api_key,
	#         "Content-Type": "application/json",
	#         "accept": "application/json",
	# 	}
	# 	if request_type not in ["post", "put", "delete"]:
	# 		request_payload = requests.get(url, headers = headers, data = payload)
	# 	elif request_type == "put":
	# 		request_payload = requests.put(url, headers = headers, data = payload)
	# 	elif request_type == "post":
	# 		request_payload = requests.post(url, headers = headers, data = payload)
	# 	elif request_type == "delete":
	# 		request_payload = requests.delete(url, headers = headers, data = payload)
	# 	time.sleep(backoff_timer)
	# 	return request_payload.json()

	def get_series(self):
		return self.api.get_series()
	
	def update_series(self, series_id, data: dict):
		return self.api.upd_series(data)
	
	def get_tags(self):
		return self.api.get_tag()
	
	def add_tag(self, tag: str):
		return self.api.create_tag(label=tag)


	# def get_series(self):
	# 	return self.sonarr_api_request(f"{self.host_url}/series")

	# def update_series(self, series_id, data: dict):
	# 	return self.sonarr_api_request(f"{self.host_url}/series/{series_id}", "put", data)

	# def get_tags(self):
	# 	return self.sonarr_api_request(f"{self.host_url}/tag")

	# def add_tag(self, tag: str):
	# 	data = json.dumps({ "label" : tag })
	# 	return self.sonarr_api_request(url=f"{self.host_url}/tag", request_type="post", data=data)
