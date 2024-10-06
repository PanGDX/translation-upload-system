import os,json, re



def load_json(file_path):
    if file_path and not file_path.endswith(".json"):
        file_path += ".json"
    
    assert('.json' in file_path)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError

def split_paragraph(text):
	midpoint = len(text) // 2
	closest_newline = text.find('\n', midpoint)

	if closest_newline == -1:
		# If no newline character is found, search backwards from the midpoint.
		closest_newline = text.rfind('\n', 0, midpoint)
		if closest_newline == -1:
			# If still no newline character, split at the midpoint.
			closest_newline = midpoint

	part1 = text[:closest_newline].strip()
	part2 = text[closest_newline:].strip()

	return part1, part2




def modify_json_file(file_path, append_json):
    def deep_merge(source, update):
        for key, value in update.items():
            if isinstance(value, dict):
                source[key] = deep_merge(source.get(key, {}), value)
            else:
                source[key] = value
        return source
    """
    @param file_path: full directory
    @param append_json: json to merge
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    merged_data = deep_merge(data, append_json)
    
    with open(file_path, 'w') as file:
        json.dump(merged_data, file, indent=4)


def submit_to_GPT(client, model:str, system_message, user_message, log:str = ""):
    completion = client.chat.completions.create(
        model=model,
        max_tokens = 4095,
        messages=[{"role": "system", "content": system_message}, 
                    {"role": "user", "content": user_message}
                    ],
    )
    if(log!=""): print(log)

    return completion.choices[0].message.content

def append_and_clean(file_path, text):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    lines = [line for line in lines if line.strip()]
    lines.append(text + '\n')
    with open(file_path, 'w') as file:
        file.writelines(lines)

def count_words(string):
    words = string.split()
    print(len(words))

def clean_filename(filename: str) -> str:
    cleaned = re.sub(r'[^\w\s\-\.\_]', '', filename)
    cleaned = cleaned.strip('.')
    return cleaned










"""
Harry Potter Please Graduate From Hogwarts Soon and Go Away
Naruto Alternative Sasuke Is Way Too Overpowered
One Piece Biggest Scum in Marine History
One Piece I Am Kaido And Luffy is Coming
One Piece Im Yamamoto Genryusai
Journalling in the MCU Characters Can Read My Diary
Cyberpunk 2077 The Legendary Life
One Piece From Flevance to the King of the World
"""