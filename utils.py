import json
from tqdm import tqdm
from collections import Counter
import numpy as np
import operator
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import pandas as pd
import networkx as nx
import base64
from collections import defaultdict
import sys,os
import math
import random
import operator
import csv
import matplotlib.pylab as pyl
import itertools
import scipy as sp
from scipy import stats
from scipy import optimize
from scipy.integrate import quad
import matplotlib.pyplot as plt 

ACCURATE_PASS = 1801
EVENT_TYPES = ['Duel', 'Foul', 'Free Kick', 'Interruption', 
             'Offside', 'Others on the ball', 'Pass', 'Shot']

TOURNAMENTS=['Italy','England','Germany', 'France', 
             'Spain', 'European_Championship','World_Cup']

data_folder='data/'
def load_public_dataset(data_folder=data_folder, tournament='Italy'):
    """
    Load the json files with the matches, events, players and competitions
    
    Parameters
    ----------
    data_folder : str, optional
        the path to the folder where json files are stored. Default: 'data/'
        
    tournaments : list, optional
        the list of tournaments to load. 
        
    Returns
    -------
    tuple
        a tuple of four dictionaries, containing matches, events, players and competitions
        
    """
    # loading the matches and events data
    matches, events = {}, {}
    with open('./data/events/events_%s.json' %tournament) as json_data:
        events = json.load(json_data)
    with open('./data/matches/matches_%s.json' %tournament) as json_data:
        matches = json.load(json_data)
    
    match_id2events = defaultdict(list)
    match_id2match = defaultdict(dict)
    for event in events:
        match_id = event['matchId']
        match_id2events[match_id].append(event)
                                         
    for match in matches:
        match_id = match['wyId']
        match_id2match[match_id] = match
                                   
    # loading the players data
    with open('./data/players.json') as json_data:
        players = json.load(json_data)
    
    player_id2player = defaultdict(dict)
    for player in players:
        player_id = player['wyId']
        player_id2player[player_id] = player
    
    # loading the competitions data
    competitions={}
    with open('./data/competitions.json') as json_data:
        competitions = json.load(json_data)
    competition_id2competition = defaultdict(dict)
    for competition in competitions:
        competition_id = competition['wyId']
        competition_id2competition[competition_id] = competition
    
    # loading the competitions data
    teams={}
    with open('./data/teams.json') as json_data:
        teams = json.load(json_data)
    team_id2team = defaultdict(dict)
    for team in teams:
        team_id = team['wyId']
        team_id2team[team_id] = team
    
    return match_id2match, match_id2events, player_id2player, competition_id2competition, team_id2team

def get_weight(position):
    """
    Get the probability of scoring a goal given the position of the field where 
    the event is generated.
    
    Parameters
    ----------
    position: tuple
        the x,y coordinates of the event
    """
    x, y = position
    
    # 0.01
    if x >= 65 and x <= 75:
        return 0.01
    
    # 0.5
    if (x > 75 and x <= 85) and (y >= 15 and y <= 85):
        return 0.5
    if x > 85 and (y >= 15 and y <= 25) or (y >= 75 and y <= 85):
        return 0.5
    
    # 0.02
    if x > 75 and (y <= 15 or y >= 85):
        return 0.02
    
    # 1.0
    if x > 85 and (y >= 40 and y <= 60):
        return 1.0
    
    # 0.8
    if x > 85 and (y >= 25 and y <= 40 or y >= 60 and y <= 85):
        return 0.8
    
    return 0.0


def in_window(events_match, time_window):
    start, end = events_match[0], events[-1]
    return start['eventSec'] >= time_window[0] and end['eventSec'] <= time_window[1]



def segno(x):
    """
    Input:  x, a number
    Return:  1.0  if x>0,
            -1.0  if x<0,
             0.0  if x==0
    """
    if   x  > 0.0: return 1.0
    elif x  < 0.0: return -1.0
    elif x == 0.0: return 0.0

def standard_dev(list):
    ll = len(list)
    m = 1.0 * sum(list)/ll
    return ( sum([(elem-m)**2.0 for elem in list]) / ll )**0.5

def list_check(lista):
    """
    If a list has only one element, return that element. Otherwise return the whole list.
    """
    try:
        e2 = lista[1]
        return lista
    except IndexError:
        return lista[0]
    

def get_event_name(event):
    event_name = ''
    try:
        if event['subEventName'] != '':
            event_name = event_names_df[(event_names_df.event == event['eventName']) & (event_names_df.subevent == event['subEventName'])].subevent_label.values[0]
        else:
            event_name = event_names_df[event_names_df.event == event['eventName']].event_label.values[0]
    except TypeError:
        #print event
        pass
    
    return event_name
    
def is_in_match(player_id, match):
    team_ids = list(match['teamsData'].keys())
    all_players = []
    for team in team_ids:
        in_bench_players = [m['playerId'] for m in match['teamsData'][team]['formation']['bench']]
        in_lineup_players = [m['playerId'] for m in match['teamsData'][team]['formation']['lineup']]
        substituting_players = [m['playerIn'] for m in match['teamsData'][team]['formation']['substitutions']]
        all_players += in_bench_players + in_lineup_players + substituting_players
    return player_id in all_players


def data_download():
    """
    Downloading script for soccer logs public open dataset:
    https://figshare.com/collections/Soccer_match_event_dataset/4415000/2
    Data description available here:
    Please cite the source as:
    Pappalardo, L., Cintia, P., Rossi, A. et al. A public data set of spatio-temporal match events in soccer competitions. 
    Scientific Data 6, 236 (2019) doi:10.1038/s41597-019-0247-7, https://www.nature.com/articles/s41597-019-0247-7
    """

    import requests, zipfile, json, io


    dataset_links = {

    'matches' : 'https://ndownloader.figshare.com/files/14464622',
    'events' : 'https://ndownloader.figshare.com/files/14464685',
    'players' : 'https://ndownloader.figshare.com/files/15073721',
    'teams': 'https://ndownloader.figshare.com/files/15073697',
    'competitions': 'https://ndownloader.figshare.com/files/15073685'
    }

    print ("Downloading matches data")
    r = requests.get(dataset_links['matches'], stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("data/matches")

    
    print ("Downloading teams data")
    r = requests.get(dataset_links['teams'], stream=False)
    print (r.text, file=open('data/teams.json','w'))


    print ("Downloading players data")
    r = requests.get(dataset_links['players'], stream=False)
    print (r.text, file=open('data/players.json','w'))
    
    print ("Downloading competitions data")
    r = requests.get(dataset_links['competitions'], stream=False)
    print (r.text, file=open('data/competitions.json','w'))
    
    print ("Downloading events data")
    r = requests.get(dataset_links['events'], stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("data/events")
    
    print ("Download completed")


