from protorpc import messages
from google.appengine.ext import ndb
import endpoints
import random

class User(ndb.Model):
	"""User profile"""
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty()

class Game(ndb.Model):
	"""Game object"""
	user1 = ndb.KeyProperty(required=True, kind='User')
	user2 = ndb.KeyProperty(required=False, kind='User')
	game_over = ndb.BooleanProperty(required=True, default=False)
	moves_remaining = ndb.IntegerProperty(required=True, default=9)
	grid = ndb.StringProperty(repeated=True)
	players_turn = ndb.StringProperty(required=True)
	winner = ndb.StringProperty()
	loser = ndb.StringProperty()
	draw = ndb.BooleanProperty(default=False)
		
	@classmethod
	def new_game(cls, user1, user2, game_over, moves_remaining, grid):
		"""Creates and returns a new game"""
		game = Game(user1=user1,
				user2=user2,
		        game_over=game_over,
		        moves_remaining=moves_remaining,
		        grid=grid,
		        players_turn = user1.get().name)
		game.put()
		return game
	
	def to_form(self, message):
		"""Returns a GameForm representation of the Game"""
		form = GameForm()
		form.message = message
		form.urlsafe_key = self.key.urlsafe()
		form.game_over = self.game_over
		form.moves_remaining = str(self.moves_remaining)
		form.user_name1 = self.user1.get().name
		try:
			form.user_name2 = self.user2.get().name
		except:
			form.user_name2 = ""
		form.grid = self.grid
		form.players_turn = self.players_turn
		form.winner = self.winner
		form.loser = self.loser
		form.draw = self.draw
		return form
	
	def update_grid(self,message,pos,player,valid_move):
		"""Update grid in Game object"""
		form = MoveForm()
		form.urlsafe_key = self.key.urlsafe()
		form.message = message

		#update grid if valid move
		if valid_move == True:
			#update grid with player name
			self.grid[pos] = player
			#decrement number of moves remaining
			self.moves_remaining -= 1

			#check if move results in win
			if self.check_winner(self.grid,player) == True:
				#set game_over property in Game object to True
				self.game_over = True
				form.message = "{0} wins! Game Over.".format(player)
				#set winner and loser property in Game object to the winning player
				self.winner = player
				if self.winner == self.user1.get().name:
					if self.user2 != None:
						self.loser = self.user2.get().name
					else:
						self.loser = '<Computer>'
				else:
					self.loser = self.user1.get().name
				#end game
				self.end_game(self.winner, self.loser, 9-self.moves_remaining, False)
			elif self.check_winner(self.grid,player) == False \
			and self.moves_remaining == 0:
				#end game in draw
				self.end_game(self.winner, self.loser, 9-self.moves_remaining, True)
				#set winner and loser to None since it was a draw
				self.winner = 'None'
				self.loser = 'None'
				#set draw to True
				self.draw = True

			#check if GameHistory object exists
			game = GameHistory.query(GameHistory.game == self.key).fetch()
			if game:
				for g in game:
					#append move to move_history in GameHistory object
					g.move_history.append(str({"user":player,"position":pos,"game_over":self.game_over,"draw":self.draw}))
					#save GameHistory object
					g.put()
			else:
				#create GameHistory object for game
				game = GameHistory(game=self.key,\
					move_history=[str({"user":player,"position":pos,"game_over":self.game_over,"draw":self.draw})])
				#save GameHistory object
				game.put()

				#change player_turn variable
			if self.players_turn == self.user1.get().name:
				#for two player game
				if self.user2 != None:
					self.players_turn = self.user2.get().name
				#for single player game
				else:
					self.players_turn = '<Computer>'
					if self.game_over == False:
						self.make_computer_move(self.grid)
			else:
				self.players_turn = self.user1.get().name
		
		#store form variables
		form.game_over = self.game_over
		form.players_turn = self.players_turn
		form.grid = self.grid

		#save Game object
		self.put()
		return form

	def make_computer_move(self, grid):
		empty_grid = []
		for i,x in enumerate(grid):
			if x == "":
				empty_grid.append(str(i))
				
		self.update_grid('Making Move',\
					int(random.choice(empty_grid)),\
					"<Computer>",\
					True)

	
	def check_winner(self, grid, player):
		"""check if player has a win in the grid"""
		#win horizontal
		if grid[0:3] == player:
			return True
		elif grid[3:6] == player:
			return True
		elif grid[6:9] == player:
			return True
		#win vertical
		elif grid[0] == player and grid[3] == player and grid[6] == player:
			return True
		elif grid[1] == player and grid[4] == player and grid[7] == player:
			return True
		elif grid[2] == player and grid[5] == player and grid[8] == player:
			return True
		#win diagonal
		elif grid[0] == player and grid[4] == player and grid[8] == player:
			return True
		elif grid[2] == player and grid[4] == player and grid[6] == player:
			return True
		#no winner
		else:
			return False
	
	def end_game(self, winner, loser, moves, draw=False):
		"""
		Ends the game
		If draw is True no winner
		If draw is False capture winner, loser and number of moves
		"""
		try:
			#check if user has Score object
			user = Score.query(Score.user == winner)
			winning_user = user.get()
			if draw == False:
				#store wins, number of moves
				#and calculate winning percentage
				winning_user.wins += 1
				winning_user.win_percent = \
				winning_user.wins + (winning_user.draws*.5)\
				/(winning_user.wins+winning_user.losses+winning_user.draws)
				winning_user.number_of_moves += moves
			else:
				#store draws
				winning_user.draws += 1
			#save Score object
			winning_user.put()
		except AttributeError as ae:
			#no Score object found for user
			if draw == False:
				#create Score object for user
				user = Score(user=winner,\
					wins=1,\
					win_percent=1.000,\
					number_of_moves=moves)
			else:
				#create Score object for user
				user = Score(user=winner,\
					draws=1,\
					win_percent=.500)
			#save Score object
			user.put()

		try:
			#check if user has Score object
			user = Score.query(Score.user == loser)		
			#Store loser and calculate winning_percentage
			losing_user = user.get()
			losing_user.losses += 1
			losing_user.win_percent = \
			losing_user.wins + (losing_user.draws*.5)\
			/(losing_user.wins+losing_user.losses+losing_user.draws)
			#save Score object
			losing_user.put()
		except AttributeError as ae:
			#no Score object found for user
			if draw ==False:
				#create Score object for user
				user = Score(user=loser,losses=1,win_percent=.000)
			else:
				#create Score object for user
				user = Score(user=loser,draws=1,win_percent=.500)
			#save Score object
			user.put()

	def cancel_game(self,message,authorized):
		"""
		Cancel active game
		"""
		form = CancelForm()
		
		if authorized == True:
			#set form variables for output
			form.game_over = True
		else:
			form.game_over = False
		form.urlsafe_key = self.key.urlsafe()
		form.message = message
		return form

	@classmethod
	def get_user_games(cls, message, user):
		"""
		Return list of active user games
		"""
		#set form variables
		form = UserGames()
		form.message = message
		form.user = user.get().name
		form.games = []
		
		#get games matching user
		game = Game.\
		query(ndb.OR(Game.user1 == user,\
			Game.user2 == user)).fetch()
		if game:
			for g in game:
				#only return active games
				if g.game_over == False:
					form.games.append(str(g.key.id()))
		return form
	
class GameHistory(ndb.Model):
	"""Game history object"""
	game = ndb.KeyProperty(required=True, kind='Game')
	move_history = ndb.StringProperty(repeated=True)

	@classmethod
	def get_move_history(cls, message, game):
		#query GameHistory object for requested game
		gh = GameHistory.\
		query(GameHistory.game == ndb.Key(urlsafe=game)).fetch(1)
		if gh:
			for g in gh:
				#store form variables 
				form = GameHistoryForm()
				form.message = message
				form.urlsafe_key = game
				form.move_history = g.move_history
				return form
		else:
			raise endpoints.NotFoundException('No game history for this game')


class Score(ndb.Model):
	"""Score object"""
	user = ndb.StringProperty(required=True)
	wins = ndb.IntegerProperty(default=0)
	losses = ndb.IntegerProperty(default=0)
	draws = ndb.IntegerProperty(default=0)
	win_percent = ndb.FloatProperty(default=.000)
	number_of_moves = ndb.IntegerProperty()

	@classmethod
	def get_user_rankings(cls, message, num_results):
		#get user rankings from Score object
		#store form varaibles
		form = UserRankings()
		form.user_name = []
		form.message = message
		#query Score object sorting by winning percentage descending
		#and the least amount of moves
		scores = Score.query()\
		.order(-Score.win_percent, Score.number_of_moves)\
		.fetch(num_results)
		if scores:
			for s in scores:
				#store rankings in form object
				form.user_name\
				.append(str({"name":s.user,\
					"win_percent":s.win_percent,\
					"number_of_moves":s.number_of_moves}))
		return form

class NewGameForm(messages.Message):
	"""New game request form"""
	user_name1 = messages.StringField(1, required=True)
	user_name2 = messages.StringField(2, required=False, default="")

class MakeMoveForm(messages.Message):
	"""Make move request form"""
	pos = messages.IntegerField(1, required=True)
	player = messages.StringField(2, required=True)

class GameForm(messages.Message):
	"""GameForm for outbound game state information"""
	message = messages.StringField(1, required=True)
	urlsafe_key = messages.StringField(2,required=True)
	game_over = messages.BooleanField(3, required=True)
	moves_remaining = messages.StringField(4)
	user_name1 = messages.StringField(5, required=True)
	user_name2 = messages.StringField(6, required=True)
	grid = messages.StringField(7, repeated=True)
	players_turn = messages.StringField(8)
	winner = messages.StringField(9)
	loser = messages.StringField(10)
	draw = messages.BooleanField(11)

class MoveForm(messages.Message):
	"""MoveForm for outbound move information"""
	message = messages.StringField(1, required=True)
	urlsafe_key = messages.StringField(2,required=True)
	game_over = messages.BooleanField(3, required=True)
	players_turn = messages.StringField(4,required=True)
	grid = messages.StringField(5, repeated=True)

class CancelForm(messages.Message):
	"""CancelForm to cancel game"""
	message = messages.StringField(1, required=True)
	urlsafe_key = messages.StringField(2,required=True)
	game_over = messages.BooleanField(3, required=True)

class UserGames(messages.Message):
	"""Game form for outbound game information for provided user"""
	message = messages.StringField(1, required=True)
	user = messages.StringField(2, required=True)
	games = messages.StringField(3, repeated=True)

class UserRankings(messages.Message):
	"""Score form for outbound user rankings"""
	message = messages.StringField(1, required=True)
	user_name = messages.StringField(2, repeated=True)

class GameHistoryForm(messages.Message):
	"""GameHistory form for outbound game history of user requested game"""
	message = messages.StringField(1, required=True)
	urlsafe_key = messages.StringField(2, required=True)
	move_history = messages.StringField(3, repeated=True)

class StringMessage(messages.Message):
	"""StringMessage-- outbound (single) string message"""
	message = messages.StringField(1, required=True)