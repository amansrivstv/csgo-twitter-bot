import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
import tweepy

#csv format:
row_list = ['Match_id','Date','Map','Score','K','D','A','plusBYmin','HScent', 'ADR', 'a1v5','a1v4','a1v3','a1v2','a1v1','a5k','a4k','a3k','Rating']
loss = ' 😢 '
win = ' 😎 '
death = ' ⚰ '
kill = ' ⚔ '
PATH = 'C:\Program Files (x86)\chromedriver.exe'

def get_last_save_match_id():
    with open('matches.csv', "r") as f1:
        last_line = f1.readlines()[-1]
        last_line = last_line.split(",")
        return last_line[0]


def scrape_latest_match_id():
    driver.get("https://csgostats.gg/player/76561198854377585#/matches")
    time.sleep(5)    
    print(driver.title)
    matchlink = driver.find_element_by_xpath('//*[@title="View Match"]')
    matchlink.get_attribute('href')
    match_page = matchlink.get_attribute('href')
    return match_page[27:]

def scrape_latest_match_data(latest_match_id):
    matchDict = {}
    matchDict['Match_id'] = latest_match_id
    match_link = 'https://csgostats.gg/match/' + latest_match_id

    driver.get("https://csgostats.gg/player/76561198854377585#/matches")   
    time.sleep(5) 
    elements = driver.find_elements_by_class_name("content-tab")
    scores = elements[4].text
    scores = scores.split("\n")
    score_list = scores[2]
    score_list = score_list.split(" ")
    score_list.reverse()
    matchDict['Map'] = score_list[16]
    matchDict['Score'] = score_list[15]
    matchDict['K'] = score_list[14]
    matchDict['D'] = score_list[13]
    matchDict['A'] = score_list[12]
    matchDict['plusBYmin'] = score_list[11]
    matchDict['HScent'] = score_list[10]
    matchDict['ADR'] = score_list[9]
    matchDict['a1v5'] = score_list[8]
    matchDict['a1v4'] = score_list[7]
    matchDict['a1v3'] = score_list[6]
    matchDict['a1v2'] = score_list[5]
    matchDict['a1v1'] = score_list[4]
    matchDict['a5k'] = score_list[3]
    matchDict['a4k'] = score_list[2]
    matchDict['a3k'] = score_list[1]
    matchDict['Rating'] = score_list[0]
    driver.close()
    driver.get(match_link)
    time.sleep(5)
    detail_element = driver.find_element_by_id('match-details')
    match_info = detail_element.text.split('\n')
    matchDict['Date'] = match_info[2]
    matchDict['Map'] = match_info[0]

    #write new data to csv
    try:
        with open('matches.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=row_list)
            writer.writerow(matchDict)
    except IOError:
        print("I/O error")

    return matchDict

def generate_tweet_text(matchDict):
    score = str(matchDict['Score']).split(':')
    tweet_text = 'Competitive Matchmaking: '+matchDict['Date'] +'\n'
    if(int(score[0])<int(score[1])):
        tweet_text += "Lost " + loss + matchDict['Score'] 
    elif(int(score[0])==int(score[1])):
        tweet_text += "Tied " +  matchDict['Score']
    else:
        tweet_text += "Won! " + win + matchDict['Score']
    tweet_text += ' on ' + matchDict["Map"] + " with " + matchDict['K'] + " kills"+kill + ", "+matchDict['D'] + " deaths "+death+ ", and ADR of " + matchDict['ADR']+ '\n'

    if(int(matchDict['a1v5'])>0):
        tweet_text += 'Clutched ' + matchDict['a1v5'] + ' 1 v 5!(s) ' + '\n'
    elif(int(matchDict['a1v4'])>0):
        tweet_text += 'Clutched ' + matchDict['a1v4'] + ' 1 v 4!(s) ' + '\n'
    elif(int(matchDict['a1v3'])>0):
        tweet_text += 'Clutched ' + matchDict['a1v3'] + ' 1 v 3!(s) ' + '\n'
    elif(int(matchDict['a1v2'])>0):
        tweet_text += 'Clutched ' + matchDict['a1v2'] + ' 1 v 2!(s) ' + '\n'

    if(int(matchDict['a5k'])>0):
        tweet_text += "Multikills!! " + matchDict['a5k'] + '* ACE(s) ' + '\n'
    if(int(matchDict['a4k'])>0):
        tweet_text += "Multikills!! " + matchDict['a4k'] + '* 4k!!!! ' + '\n'
    if(int(matchDict['a3k'])>0):
        tweet_text += "Multikills!! " + matchDict['a3k'] + '* 3k!!! ' + '\n'

    return tweet_text + 'For complete stats and demo gameplay ==> https://csgostats.gg/match/' + matchDict['Match_id']


def tweet_with_tweepy(tweet_text,map_name):
    api = twitter_api()
    filename = map_name + '.jpg'
    print(tweet_text)
    print(map_name)
    api.update_with_media(filename=filename , status=tweet_text, place_id=map_name)
    print("status Upadate Successfull")

def twitter_api():
    keys_file = open("keys.txt")
    lines = keys_file.readlines()
    consumer_key = lines[0].rstrip()
    consumer_secret = lines[1].rstrip()
    access_token = lines[2].rstrip()
    access_token_secret = lines[3].rstrip()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

def check_if_diffrent():
    last_save_match_id = get_last_save_match_id()
    latest_match_id = scrape_latest_match_id()
    if (last_save_match_id == latest_match_id):
        return False,latest_match_id
    else:
        return True,latest_match_id



while(True):
    driver = webdriver.Chrome(PATH)
    peek,match_id = check_if_diffrent()
    #peek = True
    #latest_match_id = scrape_latest_match_id()
    if (peek):
        matchDict = scrape_latest_match_data(latest_match_id)
        tweet_text = generate_tweet_text(matchDict)
        tweet_with_tweepy(tweet_text,matchDict['Map'])
        driver.quit()
        time.sleep(60*60)
    else:
        print("sleeping for an hour.....")
        driver.quit()
        time.sleep(60*60)
