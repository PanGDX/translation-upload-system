import os
from utility import modify_json_file

rootDir = os.path.expanduser("~/cli-tool/")
assert (os.path.exists(rootDir))

full_story_name = str(input("Full story name: "))
patreon_story_name = str(input("Patreon Category name: "))

modify_json_file(
	file_path=os.path.join(rootDir, "data.json"),
	appendJson={
		full_story_name: {
			"Next Translated Chapter": 1,
			"Next Inkstone Chapter": 1,
			"Next Patreon Chapter": 1,
			"Patreon Category": patreon_story_name
		}
	}
)