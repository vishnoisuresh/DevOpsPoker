#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
gregister_url='http://localhost:5001'
glocalip_adr='127.0.0.1'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys

from requests import put
import json

app = Flask(__name__)
api = Api(app)

# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):

    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @return a dictionary containing the following values
    #         bid  : a number between 0 and max_bid
    def __get_bid(self, data):
        
        min_bid = data['min_bid']
        big_blind = data['big_blind']
        highCards = ['A', 'K', 'Q', 'J',]
        hand = data['hand']
        board= data['board']
        print "board Value: ", board
        print "hand Value: ", hand
        print "big_blind Value: ", big_blind
        print "min_bid Value: ", min_bid
        print "Length of the board: ", len(board)
        bid = min_bid
        if len(board)==0: 
            if hand[0][0] in highCards or hand[1][1] in highCards:
                bid = min_bid + big_blind +100
            else:
                bid = min_bid+50

        if len(board)==3:
            cards = hand + board

            for x in cards:
                if x[0] in highCards:
                    bid = bid + big_blind + 10
            
            if hand[0][0] in highCards or hand[1][1] in highCards:
                bid = min_bid + big_blind + 50
                i = 0
            for x in board:
                if x[0] in highCards:
                    bid = min_bid + big_blind + 50
            else:
                bid = min_bid
            
            if self.threeOfKind(cards) == 1:
                bid = bid + 150
        print " our bid: ", bid
        
        return bid  

    def threeOfKind(self, cards):
        
        for x in cards:
            cc.append(x[0])
        c = Counter(cc)
        listU = c.values()
        three = 3
        if three in listU:
            return 1
        else:
            return 0
            
    def straight(self, cards):
        
        for x in cards:
            cc.append(x[0])

        d = {
            "1" : 
        }

        c = Counter(cc)
        listU = c.values()
        three = 3
        if three in listU:
            return 1
        else:
            return 0
    
    # -------------------------------------------------------------- do not change behind this line
    # dispatch incoming get commands
    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)

        if command_id == 'get_bid':
            return {'bid': self.__get_bid(data)}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')

# main function
def main():

    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python3 dplayer bazinga 40001 x407
        """)
        return 0


    # register player
    r = put("%s/dpoker/v1/enter_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass':api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name or password')

    else:
        print('registration successful')

    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass': api_pass}).json()
# run the main function
if __name__ == '__main__':
    main()


