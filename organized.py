"""
To Do:
- 1813 not loading last double jeopardy category (and subsequently final)
- 2955 missing clues in single jeopardy. same problem as 1813 but semi fixed
- go through and edit game type for college
- add subjects to categories
- analyze data
"""

import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
from datetime import datetime
from password import password

def getText(div):
	return div.text

def gameTypeToCode(type):
    if 'Teen Tournament' in type:
        return 'Teen'
    elif 'College Championship' in type:
        return 'College'
    elif 'Teachers Tournament' in type:
        return 'Teachers'
    elif 'Tournament of Champions' in type:
        return 'Champion'
    elif 'Celebrity Jeopardy' in type:
        return 'Celebrity'
    elif 'Power Players Week' in type:
        return 'Power'
    elif 'Kids' in type:
        return 'Kids'
    elif 'Back to School' in type:
        return 'School'
    elif 'Senior' in type:
        return 'Seniors'
    elif 'International Tournament' in type:
        return 'International'
    elif 'Armed Forces Week' in type:
        return 'Military'
    elif 'Olympic Games Tournament' in type:
        return 'Olympic'
    elif 'Greatest of All Time' in type:
        return 'Greatest'
    elif 'All-Star Games' in type:
        return 'AllStar'
    elif 'Boston' in type:
        return 'Boston'
    elif 'Battle of the Decades' in type:
        return 'Decades'
    elif 'The IBM Challenge' in type:
        return 'IBM'
    elif 'Million Dollar Masters' in type:
        return 'Masters'
    elif 'Million Dollar Celebrity Invitational' in type:
        return 'MillionCelebrity'
    elif 'Trebek Pilot' in type:
        return 'Pilot'
    elif 'Ultimate Tournament' in type:
        return 'Ultimate'
    else:
        return 'Regular'


mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd=password,
	database="JArchive",
	auth_plugin='mysql_native_password'
)

mycursor = mydb.cursor(buffered=True)

def getRound(soup, id, gameId, round):
    div = soup.find('div', id=id)
    if div:
        categories = div.find_all('td', class_="category_name")
        # f = open("soup.txt","w")
        # f.write(soup.prettify())
        # f.close()
        if len(categories) == 6:
            categories = list(map(getText, categories))
            clueDivs = div.find_all('td', class_='clue')
        else:
            categories = soup.find_all('td', class_="category_name")
            clueDivs = soup.find_all('td', class_='clue')
            if round == 'Single':
                categories = categories[:6]
                clueDivs = clueDivs[:6]
            elif len(categories) >= 12:
                categories = categories[6:12]
                clueDivs = clueDivs[6:12]
            else:
                categories = []
                clueDivs = []
            categories = list(map(getText, categories))
        
        if len(categories) > 0:
            clues = [[0 for x in range(6)] for y in range(5)]
            answers = [[0 for x in range(6)] for y in range(5)]
            extract = re.compile('correct_response&quot;&gt;(.*)&lt;/em&gt;')

            row = 0
            col = 0
            numClues = 0

            for square in clueDivs:
                text = square.find('td', class_='clue_text')
                if text:
                    clues[row][col] = text.text
                    numClues += 1
                answerDiv = square.find('div')
                if answerDiv:
                    answer = extract.search(str(answerDiv))
                    pretty = BeautifulSoup(answer.group(1), 'html.parser').text
                    if pretty.startswith('<i>'):
                        pretty = pretty[3:]
                    if pretty.endswith('</i>'):
                        pretty = pretty[:-4]
                    answers[row][col] = pretty
                col += 1
                if col == 6:
                    col = 0
                    row += 1

            for col in range(6):
                sql = "INSERT INTO Categories (GameId, RoundCode, Name) VALUES (%s, %s, %s)"
                val = (gameId, round, categories[col])
                mycursor.execute(sql, val)
                mydb.commit()
                categoryId = mycursor.lastrowid

                sql = "Insert Into Clues (Categoryid, PointVal, Clue, Answer) Values (%s, %s, %s, %s)"
                val = []
                for row in range(5):
                    val.append((categoryId, row * 200 + 200, clues[row][col], answers[row][col]))
                mycursor.executemany(sql, val)
                mydb.commit()
            
            print('\t', round, ': ', numClues)
        else:
            print('\t', round, ': no clues')

def getFinal(soup, gameId):
    div = soup.find('div', id='final_jeopardy_round')
    if div:
        print('\t Final Jeopardy')
        category = div.find('td', class_='category_name').text
        clueDiv = div.find('td', class_='clue')
        clue = clueDiv.find('td', class_='clue_text').text
        answer = div.find('td', class_='category')
        extract = re.compile('correct_response(.*)&lt;/em&gt;') 
        answer = extract.search(str(answer.find('div')))
        answer = answer.group(1)[11:]
        answer = BeautifulSoup(answer, 'html.parser').text
        answer = answer.replace('<i>', '')
        answer = answer.replace('</i>', '')
        
        sql = "Insert Into Categories (GameId, RoundCode, Name) Values (%s, %s, %s)"
        val = (gameId, 'Final', category)
        mycursor.execute(sql, val)
        mydb.commit()
        categoryId = mycursor.lastrowid

        sql = "Insert Into Clues (CategoryId, PointVal, Clue, Answer) Values (%s, %s, %s, %s)"
        val = (categoryId, 0, clue, answer)
        mycursor.execute(sql, val)
        mydb.commit()

        tieCategory = div.find_all('td', class_='category_name')
        if len(tieCategory) == 2:
            print('\t Tie breaker')
            tieCategory = tieCategory[1]
            clueDiv = div.find_all('td', class_='clue')[1]
            clue = clueDiv.find('td', class_='clue_text').text
            answer = div.find_all('td', class_='category')[1]
            answer = extract.search(str(answer.find('div')))
            answer = answer.group(1)[11:]
            answer = BeautifulSoup(answer, 'html.parser').text
            answer = answer.replace('<i>', '')
            answer = answer.replace('</i>', '')
            
            sql = "Insert Into Categories (GameId, RoundCode, Name) Values (%s, %s, %s)"
            val = (gameId, 'Tie', category)
            mycursor.execute(sql, val)
            mydb.commit()
            categoryId = mycursor.lastrowid

            sql = "Insert Into Clues (CategoryId, PointVal, Clue, Answer) Values (%s, %s, %s, %s)"
            val = (categoryId, 0, clue, answer)
            mycursor.execute(sql, val)
            mydb.commit()

mycursor.execute("Select Id From Games Order By Id Desc")
latestGame = mycursor.fetchone()

if latestGame:
    latestGame = latestGame[0]
else:
    latestGame = 0

x = latestGame + 1
while True:
    gameId = str(x).zfill(4)
    url = 'http://www.j-archive.com/showgame.php?game_id=' + gameId
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    if (soup.find(class_="error")):
        break
    gameType = soup.find(id="game_comments").text
    gameType = gameTypeToCode(gameType)

    gameDate = soup.find(id="game_title").find('h1').text
    gameDate = gameDate.split(' - ')[1]
    gameDate = datetime.strptime(gameDate, '%A, %B %d, %Y').date()

    sql = "INSERT INTO Games (Id, Date, TypeCode) VALUES (%s, %s, %s)"
    val = (gameId, gameDate, gameType)
    print(val)
    mycursor.execute(sql, val)

    mydb.commit()

    getRound(soup, 'jeopardy_round', gameId, 'Single')
    getRound(soup, 'double_jeopardy_round', gameId, 'Double')
    getFinal(soup, gameId)

    x += 1