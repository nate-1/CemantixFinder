from bs4 import BeautifulSoup
import requests
import timeit
import sys
from termcolor import colored


ENGLISH_ASSOC_ENDPOINT = "https://wordassociations.net/en/words-associated-with/"
FRENCH_ASSOC_ENDPOINT = "https://wordassociations.net/fr/associations-avec-le-mot/"

ENGLISH_GAME_ENDPOINT = "https://cemantle.herokuapp.com/score"
FRENCH_GAME_ENDPOINT = "https://cemantix.herokuapp.com/score"

LANG = sys.argv[1]

MIN_SCORE_TO_USE_ASSOC = float(sys.argv[2])

WIN_SCORE = float('1.0')

S = requests.Session()

def getAssociaions(word, start):
    requestUrl =""
    if LANG == "en":
        requestUrl = ENGLISH_ASSOC_ENDPOINT + word
    elif LANG == "fr":
        requestUrl = FRENCH_ASSOC_ENDPOINT + word
    else: 
        raise Exception("Language not supported")

    requestUrl += '?start=' + str(start) 

    r = S.get(requestUrl)
    soup = BeautifulSoup(r.content, 'html.parser')
    mainDiv = soup.find('div', attrs={'class': 'n-content'})
    lis = mainDiv.find_all('li')
    if lis is None or len(lis) == 0:
        raise Exception('no words found')
    arrayOut = []
    for li in lis:
        arrayOut.append(li.findChildren('a')[0].text)
    return arrayOut

def checkWord(word):  
    requestUrl = ""
    if LANG == "en":
        requestUrl = ENGLISH_GAME_ENDPOINT
    elif LANG == "fr":
        requestUrl = FRENCH_GAME_ENDPOINT
    else:
        raise Exception("Language not supported")
    
    r = S.post(requestUrl, data={'word': word})
    j = r.json()
    if(j.get('error') is not None):
        raise Exception()
    return float(j['score'])


if __name__ == "__main__":
    start = timeit.default_timer()
    filename = ""
    f = open(LANG + '.txt', "r")
    highestScore = -50.0000
    highestScoreWord = ""
    while True : 
        line = f.readline()
        score = 0 
        try:
            score = checkWord(line)
        except Exception: 
            continue

        if score > highestScore:
            highestScore = score
            highestScoreWord = line
            print(colored(str(score) + ' : ' + line, 'red'))
        
        if score >= MIN_SCORE_TO_USE_ASSOC:
            break   
        
    if score >= 1:
        print('word found: ' + highestScoreWord)
        exit()

    print(colored('SWITCH TO ASSOCIATIONS', 'red'))

    while True : 
        if score >= WIN_SCORE:
                stop = timeit.default_timer()
                print('word found \'' + word + '\' in ' + str(stop - start) + ' seconds')            
                exit()
    
        print(colored('ASSOC FROM: ' + highestScoreWord, 'red'))

        hasWentHigher = False
        for page in ['0', '100', '200'] :
            arrayAssoc = getAssociaions(highestScoreWord, page)

            if score >= WIN_SCORE:
                stop = timeit.default_timer()
                print('word found \'' + word + '\' in ' + str(stop - start) + ' seconds')            
                exit()


            for word in arrayAssoc:
                try:
                    score = checkWord(word.lower())
                except Exception: 
                    continue

                print(score, ' : ', word)

                if score > highestScore:
                    highestScore = score
                    highestScoreWord = word
                    hasWentHigher = True
                    print(colored(str(score) + ' : ' + word, 'red'))
                    break
            
            if hasWentHigher:
                break

        if not hasWentHigher: 
            print('Stuck in associations')
            exit()
