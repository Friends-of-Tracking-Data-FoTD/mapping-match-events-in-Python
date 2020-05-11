import pandas as pd
from collections import defaultdict
from utils import get_weight
import numpy as np

data_folder = 'data/'
tags_names_df = pd.read_csv(data_folder + 'tags2name.csv', delimiter=';')

INTERRUPTION = 5
FOUL = 2
OFFSIDE = 6
DUEL = 1
SHOT = 10
SAVE_ATTEMPT = 91
REFLEXES = 90
TOUCH = 72
DANGEROUS_BALL_LOST = 2001
MISSED_BALL = 1302
PASS = 8
PENALTY = 35
ACCURATE_PASS = 1801

END_OF_GAME_EVENT = {
    u'eventName': -1,
 u'eventSec': 7200,
 u'id': -1,
 u'matchId': -1,
 u'matchPeriod': u'END',
 u'playerId': -1,
 u'positions': [],
 u'subEventName': -1,
 u'tags': [],
 u'teamId': -1
}

START_OF_GAME_EVENT = {
    u'eventName': -2,
 u'eventSec': 0,
 u'id': -2,
 u'matchId': -2,
 u'matchPeriod': u'START',
 u'playerId': -2,
 u'positions': [],
 u'subEventName': -2,
 u'tags': [],
 u'teamId': -2
}

def is_interruption(event, current_half):
    """
    Verify whether or not an event is a game interruption. A game interruption can be due to
    a ball our of the field, a whistle by the referee, a fouls, an offside, the end of the
    first half or the end of the game.
    
    Parameters
    ----------
    event: dict
        a dictionary describing the event
        
    current_half: str
        the current half of the match (1H = first half, 2H == second half)
        
    Returns
    -------
    True is the event is an interruption
    False otherwise
    """
    event_id, match_period = event['eventName'], event['matchPeriod']
    if event_id in [INTERRUPTION, FOUL, OFFSIDE] or match_period != current_half or event_id == -1:
        return True
    return False

def is_pass(event):
    return event['eventName'] == PASS

def is_accurate_pass(event):
    return ACCURATE_PASS in [tag['id'] for tag in event['tags']]

def is_shot(event):
    """
    Verify whether or not the event is a shot. Sometimes, a play action can continue
    after a shot if the team gains again the ball. We account for this case by looking
    at the next events of the game.
    
    Parameters
    ----------
    event: dict
        a dictionary describing the event
        
    Returns
    -------
    True is the event is a shot
    False otherwise
    """
    event_id = event['eventName']
    return event_id == 10
    
def is_save_attempt(event):
    return event['subEventName'] == SAVE_ATTEMPT

def is_reflexes(event):
    return event['subEventName'] == REFLEXES

def is_touch(event):
    return event['subEventName'] == TOUCH

def is_duel(event):
    return event['eventName'] == DUEL

def is_ball_lost(event, previous_event):
    tags = get_tag_list(event)
    #if DANGEROUS_BALL_LOST in tags or MISSED_BALL in tags:
    #    return True
    #if event['eventName'] == PASS:
    #    if 'Not accurate' in tags:
    #        return True
    if event['teamId'] != previous_event['teamId'] and previous_event['teamId'] != -2 and event['eventName'] != 1:
        return True
    
    return False

def is_penalty(event):
    return event['subEventName'] == PENALTY

def get_tag_list(event):
    return [tags_names_df[tags_names_df.Tag == tag['id']].Description.values[0] for tag in event['tags']]

def pre_process(events):
    """
    Duels appear in pairs in the streamflow: one event is by a team and the other by
    the opposing team. This can create
    """
    filtered_events, index, prev_event = [], 0, {'teamId': -1}
    
    while index < len(events) - 1:
        current_event, next_event = events_match[index], events_match[index + 1]
        
        # if it is a duel
        if current_event['eventName'] == DUEL: 
            
            if current_event['teamId'] == prev_event['teamId']:
                filtered_events.append(current_event)
            else:
                filtered_events.append(next_event)
            index += 1
            
        else:
            # if it is not a duel, just add the event to the list
            filtered_events.append(current_event)
            prev_event = current_event
            
        index += 1
    return filtered_events


def get_play_actions(match_id2events, match_id, verbose=False):
    """
    Given a list of events occuring during a game, it splits the events
    into play actions using the following principle:
    
    - an action begins when a team gains ball possession
    - an action ends if one of three cases occurs:
    -- there is interruption of the match, due to: 1) end of first half or match; 2) ball 
    out of the field 3) offside 4) foul
    
    """
    try:
        events_match = match_id2events[match_id]
        half_offset = {'2H' : max([x['eventSec'] for x in events_match if x['matchPeriod']=='1H']),
                      '1H':0}
        events_match = sorted(events_match, key = lambda x: x['eventSec'] + half_offset[x['matchPeriod']])
        ## add a fake event representing the start and end of the game
        events_match.insert(0, START_OF_GAME_EVENT)
        events_match.append(END_OF_GAME_EVENT)

        play_actions = []

        time, index, current_action, current_half = 0.0, 1, [], '1H'
        previous_event = events_match[0]
        while index < len(events_match) - 2:

            current_event = events_match[index]

            # if the action stops by an game interruption
            if is_interruption(current_event, current_half):
                current_action.append(current_event)
                play_actions.append(('interruption', current_action))
                current_action = []

            elif is_penalty(current_event):
                next_event = events_match[index + 1]

                if is_save_attempt(next_event) or is_reflexes(next_event):
                    index += 1
                    current_action.append(current_event)
                    current_action.append(next_event)
                    play_actions.append(('penalty', current_action))
                    current_action = []
                else:
                    current_action.append(current_event)

            elif is_shot(current_event):
                next_event = events_match[index + 1]

                if is_interruption(next_event, current_half):
                    index += 1
                    current_action.append(current_event)
                    current_action.append(next_event)
                    play_actions.append(('shot', current_action))
                    current_action = []

                ## IF THERE IS A SAVE ATTEMPT OR REFLEXES; GO TOGETHER
                elif is_save_attempt(next_event) or is_reflexes(next_event):
                    index += 1
                    current_action.append(current_event)
                    current_action.append(next_event)
                    play_actions.append(('shot', current_action))
                    current_action = []

                else:
                    current_action.append(current_event)
                    play_actions.append(('shot', current_action))
                    current_action = []

            elif is_ball_lost(current_event, previous_event):

                current_action.append(current_event)
                play_actions.append(('ball lost', current_action))
                current_action = [current_event]

            else:
                current_action.append(current_event)

            time = current_event['eventSec']
            current_half = current_event['matchPeriod']
            index += 1

            if not is_duel(current_event):
                previous_event = current_event

        events_match.remove(START_OF_GAME_EVENT)
        events_match.remove(END_OF_GAME_EVENT)

        return play_actions
    except TypeError:
        return []
    
def get_invasion_index(tournaments, events, match_id, lst=False):
    """
    Compute the invasion index for the input match
    
    Parameters
    ----------
    tournaments : list
        the list of tournaments
    
    events : list
        list of all events
    
    match_id: int
        the match_id of the match for which we want the invasion index
        
    Returns
    -------
    float
        the invasion index of the two teams, the list of invasion acceleration 
        for each possesion phase of each team
    """
    # get the actions in the match
    actions = get_play_actions(tournaments, events, match_id)
    team2invasion_index = defaultdict(list)
    team2invasion_speed = defaultdict(list)
    
    events_match = []
    for tournament in tournaments:
        for event in events[tournament]:
            if event['matchId'] == match_id:
                events_match.append(event)
                
    half_offset = {'2H': max([x['eventSec'] for x in events_match if x['matchPeriod']=='1H']),
                      '1H':0}
    events_match = sorted(events_match, key = lambda x: x['eventSec'] + half_offset[x['matchPeriod']])
    off = half_offset['2H']
    times_all = []
    # for each action
    for action in actions:
        action_type, events_match = action
        offset = off if events_match[0]['matchPeriod']=='2H' else 0
        if len(set([x['matchPeriod'] for x in events_match])) > 1:
            continue
        team_id = events_match[0]['teamId']
        all_weights, times = [], []
        for event in events_match:
            try:
                x, y, s = int(event['positions'][0]['x']), int(event['positions'][0]['y']), event['eventSec']
            except:
                continue #skip to next event in case of missing position data
            all_weights.append(get_weight((x, y)))
            #all_weights.append(get_datadriven_weight((x, y)))
            times.append(s)

        times_maxinv = sorted(times,key=lambda x:all_weights[times.index(x)],reverse=True)[0]
        seconds = times_maxinv-events_match[0]['eventSec']
        if seconds > 0.8:
            team2invasion_speed[team_id]+= [(events_match[0]['eventSec']+offset,(np.max(all_weights)-all_weights[0]) / seconds**2) ]
        
        team2invasion_index[team_id] += [(events_match[0]['eventSec']+offset,np.max(all_weights))]
    
    if not lst:
        team2invasion_index={k:[x for x in v] for k,v in team2invasion_index.items()}
        team2invasion_speed={k:[x for x in v] for k,v in team2invasion_speed.items()}
    
    return team2invasion_index, team2invasion_speed

