import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import(User,
	Game,
	Score,
	NewGameForm,
	GameForm,
	MakeMoveForm,
	MoveForm,
	CancelForm,
	UserGames,
	UserRankings,
	GameHistoryForm,
	GameHistory,
	StringMessage)

from utils import get_by_urlsafe

#request form variables
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

GET_GAME_REQUEST = \
endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)

GET_USER_GAMES_REQUEST = \
endpoints.ResourceContainer(\
	user = messages.StringField(1,required=True),)

CANCEL_GAME_REQUEST = \
endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),\
 user = messages.StringField(2,required=True),)

MAKE_MOVE_REQUEST = \
endpoints.ResourceContainer(MakeMoveForm,\
 urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = \
endpoints.ResourceContainer(user_name=messages.StringField(1),\
 email=messages.StringField(2))

USER_RANKINGS_REQUEST =  \
endpoints.ResourceContainer(num_results=messages.IntegerField(1))

GAME_HISTORY_REQUEST =  \
endpoints.ResourceContainer(\
	urlsafe_game_key=messages.StringField(1, required=True))

@endpoints.api(name='tictactoe', version='v1')
class TicTacToeApi(remote.Service):
	"""Game API"""

	@endpoints.method(request_message=USER_REQUEST,
		response_message=StringMessage,
		path='user',
		name='create_user',
		http_method='POST')
	def create_user(self,request):
		"""Create a User. Requires a unique username"""
		if User.query(User.name == request.user_name).get():
			raise endpoints.ConflictException(
				'A User with that name already exists!')
		#do not allow creation of reserved <Computer> username
		if request.user_name.upper() == '<COMPUTER>':
			raise endpoints.ConflictException(
				'The requested name is not acceptable')
		user = User(name=request.user_name, email=request.email)
		user.put()
		return StringMessage(message='User {} created!'.\
			format(request.user_name))

	@endpoints.method(request_message=NEW_GAME_REQUEST,
		response_message=GameForm,
		path='game',
		name='new_game',
		http_method='POST')
	def new_game(self, request):
		"""Creates new game"""
		#query user if not found raise exception
		user1 = User.query(User.name == request.user_name1).get()
		if not user1:
			raise endpoints.NotFoundException("User 1 doesn't exist")
		
		#if user_name2 request exists query User
		if request.user_name2 != "":
			#query user if not found raise exception
			user2 = User.query(User.name == request.user_name2).get()
			if not user2:
				raise endpoints.NotFoundException("User 2 doesn't exist")

			#create Game object two player
			game = \
			Game.new_game(\
				user1.key,user2.key,False,9,["","","","","","","","",""])
		#create Game object single player
		else:
			#create Game object
			game = \
			Game.new_game(\
				user1.key,None,False,9,["","","","","","","","",""])
		return game.to_form('Good luck playing Tic Tac Toe!')

	@endpoints.method(request_message=GET_GAME_REQUEST,
		response_message=GameForm,
		path='game/{urlsafe_game_key}',
		name='get_game',
		http_method='GET')
	def get_game(self, request):
		"""Query requested game"""
		game = get_by_urlsafe(request.urlsafe_game_key,Game)
		if game:
			return game.to_form('Game Information')
		else:
			raise endpoints.NotFoundException('Game not found!')

	@endpoints.method(request_message=MAKE_MOVE_REQUEST,
		response_message=MoveForm,
		path='game/{urlsafe_game_key}',
		name='make_move',
		http_method='POST')
	def make_move(self, request):
		"""Make move in active game"""
		#query game object
		game = get_by_urlsafe(request.urlsafe_game_key, Game)

		if game:
			#check if game is over or no more moves are remaining
			if game.game_over == True or game.moves_remaining == 0:
				return game.\
				update_grid('Game already over!',\
					request.pos,\
					request.player,\
					False)
			#if position provided is out of range
			elif request.pos > 8 or request.pos < 0:
				return game.\
				update_grid('Invalid move!',\
					request.pos,\
					request.player,\
					False)
			#if grid is not empty string position is occupied
			elif game.grid[request.pos] != "":
				return game.update_grid('Position already occupied!',\
					request.pos,\
					request.player,\
					False)
			else:
				#only update if it is the players turn
				if game.players_turn == request.player:
					return game.update_grid('Making Move',\
						request.pos,\
						request.player,\
						True)
				else:
					return game.update_grid('Not the requested users turn.',\
						request.pos,\
						request.player,\
						False)
		else:
			raise endpoints.NotFoundException('Game not found!')

	@endpoints.method(request_message=CANCEL_GAME_REQUEST,
		response_message=CancelForm,
		path='game/{urlsafe_game_key}/cancel',
		name='cancel_game',
		http_method='POST')
	def cancel_game(self, request):
		"""Cancel active game"""	
		try:
			#get game object
			game = get_by_urlsafe(request.urlsafe_game_key, Game)
			if game:
				#only cancel game is user is playing that game and
				#and the game is not over
				if (game.user1.get().name == request.user\
				or  game.user2.get().name == request.user)\
				and game.game_over == False:
				 	#if there is a GameHistory object delete from object
				 	gh = GameHistory.query(GameHistory.game == \
				 		ndb.Key(urlsafe=request.urlsafe_game_key)).fetch()
				 	if gh:
				 		for g in gh:
				 			g.key.delete()
				 
					#cancel game object form data store
				 	game.key.delete()
					
					return game.\
					cancel_game('{0} canceled game {1}'.\
						format(request.user,request.urlsafe_game_key), True)
				else:
					return game.\
					cancel_game('{0} not authorized to cancel game'.\
						format(request.user),False)
		except Exception:
			return game.\
			cancel_game('Issue canceling game.',False)


	@endpoints.method(request_message=GET_USER_GAMES_REQUEST,
		response_message=UserGames,
		path='games/{user}',
		name='get_user_games',
		http_method='GET')
	def get_user_games(self, request):
		"""Get the active games for a given user"""
		#check if user exists
		user = User.query(User.name == request.user).get()
		if user:
			return Game.get_user_games('User exists', user.key)
		else:
			raise endpoints.NotFoundException('User does not exist')

	@endpoints.method(request_message=USER_RANKINGS_REQUEST,
		response_message=UserRankings,
		path='scores',
		name='get_user_rankings',
		http_method='GET')
	def get_user_rankings(self, request):
		"""Get a list of user rankings by winning percentage"""
		return Score.get_user_rankings('User Rankings',request.num_results)

	@endpoints.method(request_message=GAME_HISTORY_REQUEST,
		response_message=GameHistoryForm,
		path='history',
		name='get_game_history',
		http_method='GET')
	def get_game_history(self, request):
		"""See a list of the history of moves for a given game"""
		game = get_by_urlsafe(request.urlsafe_game_key, Game)
		if game:
			#query GameHIstory object for a given game
			return GameHistory.\
			get_move_history('Game History', request.urlsafe_game_key)
			pass
		else:
			raise endpoints.NotFoundException('Game does not exist')

api = endpoints.api_server([TicTacToeApi])

