import os
import requests
import re
import glob

import pytesseract
import pdf2image

import keys

# anki_collection_path = os.path.join(keys.anki_home, "collection.anki2")
dictionary_api_endpoint = "https://www.dictionaryapi.com/api/v3/references/medical/json"

# USE API HERE FOR DICTIONARY
def getDefinitions(word):
	request_url = dictionary_api_endpoint + '/' + word + "?key=" + keys.medical_dict_api_key
	# print(request_url)
	response = requests.get(request_url)

	# print(response.json()[0])

	if response.status_code == 200:
		try:
			return response.json()[0]["shortdef"]
		except:
			return ["TBA"]

	# Parse it for error etc.
	# if there is 

	return Exception("Error while getting definitions: ")

# Parse the format of the page for words
# Maybe put in some error handling
def parseWords(text):
	p = "^(.*) \(.*\)*"
	matches = re.findall(p, text, flags=re.MULTILINE)

	# print('\n'.join(matches))
	# if not bool(match):
	# 	return "ERROR: could not match text(" + text + ") with regex: " + p

	return matches

def filterWordsAndDefs(text):
	#  and re.match("^[\w\-/\s]+")
	filtered_text = list(filter(lambda x: x and 
		not re.match("^\s*$", x) and re.match("^[a-zA-Z,\-/\s]+$", x), text.split("\n")))
	print(filtered_text)

	return filtered_text

scan_paths = glob.glob(os.path.join(keys.scan_path, "*.pdf")) # PATH TO PDFS?? GOOGLE DOCS MAYBE
for scan_path in scan_paths:
	pages = pdf2image.convert_from_path(scan_path, 500)
	file_name = os.path.splitext(os.path.basename(scan_path))[0]
	words = []
	word_and_defs = []

	for page_num, img in enumerate(pages):
		text = pytesseract.image_to_string(img, lang='eng')

		# process text to remove pronunciation
		# print(text)

		if re.match(".*_def", file_name):
			# parse the words and definitions
			word_and_defs.extend(filterWordsAndDefs(text))
		else:
			words.extend(parseWords(text))
	print(len(words))
	# print(word_and_defs)
	print(len(word_and_defs))

	# write to a file and then import
	with open(file_name + ".txt", "w") as text_file:
		for word in words:
			definitions = getDefinitions(word)
			card_line = word + "\t" + '<br>'.join(definitions) + "\n"
			print(card_line)

			text_file.write(card_line)
		for word_or_def in word_and_defs:
			text_file.write(word_or_def + "\n")


# use ankiconnect api to make flash cards 