## Overview
A simple script that queries sonarr's API for genre info. 

## How it Works
The tooling does the following:
* clones a copy of anidb's database and uses the minified json version provided to look up tags per show
* looks up all your shows in sonarr and parses out their genres into tags
* aggregates the two together, after using find and replaces **tagging.replacements**, and drops unwanted tags stored in **tagging.drop**. Both are completely optional and can be provided in a **config.yaml** file.
* tags are then written using sonarr's API as tags; the intended use-case is to make these available for additional automation. An idea I've been toying with is dynamically assigning root folders based on genre and this will make that a lot easier to do.

## Configuration Parameters
The following parameters are required as envars (when I have a helm chart together these should be provided as sensitive values):

* **SONARR_URL**, defaults to **http://127.0.0.1:8989/api**. Please do ensure the /api is provided along with http/https being specified
* **SONARR_API**, the API key for sonarr.

Although not required, the functionality is rather nice of being able to drop unwanted items and replace specific tags; particularly for anime, **anidb** mostly gives a nice curated list, but sometimes the classificaitons are either redundant, inaccurate, or just don't make sense.

Additionally, you can optionally configure a **config.yaml**. The tooling will parse the following keys if provided:
* **tagging.drop**. This should be a list of strings of any tags you do not want to parse at all. Any values provided here will not write as tags
* * **tagging.replacements**. This can optionally be provided as a dictionary of key value pairs, with the key being replaced by the value provided. Given that cases exist where a key may have multiple values that are valid, I may retool this section to be a bit more versatile. For now though this is what I put together and it does work.

## Roadmap / Upcoming
This was thrown together over the weekend and I would not call it refined just yet. The following items are likely on the horizon, I'm open to PR's with additional feature ideas and improvements:
* tighter input validation that eliminates the need for try/except
* rate limit handling / control of pace on how hard sonarr's API can be hit
* better logging
* general performance improvements
