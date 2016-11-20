#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import TicTacToeApi
from models import Game, User

class SendReminderEmail(webapp2.RequestHandler):
	"""Send a reminder email about the game"""
	def get(self):
		app_id = app_identity.get_application_id()
		#query active user games
		games = Game.query(Game.game_over == False).fetch()

		if games:
			#loop through games
			for g in games:
				#send email letting them know it is their turn to make a move
				email = self.getUserEmail(g.players_turn)
				subject = "This is a reminder! Game: {0}".\
				format(g.key.urlsafe())
				body = 'Hello {}, it is your turn!  Please make a move.'.\
				format(g.players_turn)
				mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
					email,
					subject,
					body)
	
	def getUserEmail(self,player):
		#query users email
		user = User.query(ndb.AND(User.name == player, User.email != None))\
		.fetch(1)
		if user:
			for u in user:
				return u.email


app = webapp2.WSGIApplication([
	('/crons/send_reminder',SendReminderEmail)
	], debug=True)
