"""
To Do:
- next step: save to mysql
"""

import requests
import pprint
from bs4 import BeautifulSoup
import re
import csv

def getText(div):
	return div.text

id = input('Game id: ')
url = 'http://www.j-archive.com/showgame.php?game_id=' + id
page = requests.get(url)
# pprint.pprint(page.content)
soup = BeautifulSoup(page.content, 'html.parser')
# print(soup.prettify())
gameType = soup.find(id="game_comments").text
# if gameType:
# 	gameType = gameType.text
# else:
# 	gameType = ''
gameDate = soup.find(id="game_title").find('h1').text
gameDate = gameDate.split(' - ')[1]
categories = soup.find_all('td', class_='category_name')
if categories:
	print(len(categories))
sjCategories = categories[:6]
sjCategories = list(map(getText, sjCategories))
djCategories = categories[6:-1]
djCategories = list(map(getText, djCategories))
fjCategory = categories[-1].text
clues = soup.find_all('td', class_='clue')
sjDivs = clues[:30]
djDivs = clues[30:-1]
fjDiv = clues[-1]
extract = re.compile('correct_response&quot;&gt;(.*)&lt;/em&gt;')

sjClues = [[0 for x in range(6)] for y in range(5)]
djClues = [[0 for x in range(6)] for y in range(5)]
sjAnswers = [[0 for x in range(6)] for y in range(5)]
djAnswers = [[0 for x in range(6)] for y in range(5)]
row = 0
col = 0

for square in sjDivs:
	text = square.find('td', class_='clue_text')
	if text:
		sjClues[row][col] = text.text
	answerDiv = square.find('div')
	if answerDiv:
		answer = extract.search(str(answerDiv))
		pretty = BeautifulSoup(answer.group(1), 'html.parser').text
		if pretty.startswith('<i>'):
			pretty = pretty[3:]
		if pretty.endswith('</i>'):
			pretty = pretty[:-4]
		sjAnswers[row][col] = pretty
	col += 1
	if col == 6:
		col = 0
		row += 1

row = 0
col = 0
for square in djDivs:
	text = square.find('td', class_='clue_text')
	if text:
		djClues[row][col] = text.text
	answerDiv = square.find('div')
	if answerDiv:
		answer = extract.search(str(answerDiv))
		pretty = BeautifulSoup(answer.group(1), 'html.parser').text
		pretty = pretty.replace('<i>', '')
		pretty = pretty.replace('</i>', '')
		djAnswers[row][col] = pretty
	col += 1
	if col == 6:
		col = 0
		row += 1

fjClue = fjDiv.find('td', class_='clue_text').text
fjAnswer = soup.find_all('td', class_='category')[-1]
fjExtract = re.compile('correct_response(.*)&lt;/em&gt;')
fjAnswer = fjExtract.search(str(fjAnswer.find('div')))
fjAnswer = fjAnswer.group(1)[11:]
fjAnswer = BeautifulSoup(fjAnswer, 'html.parser').text
fjAnswer = fjAnswer.replace('<i>', '')
fjAnswer = fjAnswer.replace('</i>', '')

# for rows in range(5):
# 	for cols in range(6):
# 		print('Category:', djCategories[cols].text)
# 		print('Clue:', djClues[rows][cols])
# 		print('Answer:', djAnswers[rows][cols])
# 		print('\n')

print(gameType)
print(gameDate)
print('Category:', fjCategory)
print('Clue:', fjClue)
print('Answer:', fjAnswer)

with open('practice.csv', mode='w') as testFile:
	write = csv.writer(testFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	write.writerow([gameType])
	write.writerow([gameDate])
	write.writerow([])
	write.writerow(['Single Jeopardy'])
	write.writerow([''] + sjCategories + [''] + sjCategories)
	for x in range(5):
		write.writerow([200*x + 200] + sjClues[x] + [''] + sjAnswers[x])
	write.writerow([])
	write.writerow(['Final Jeopardy'])
	write.writerow([fjCategory])
	write.writerow([fjClue])
	write.writerow([fjAnswer])
