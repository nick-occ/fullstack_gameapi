#TicTacToe API#

##Description##
This API will allow developers to develop a front-end TicTacToe application by accessing functions created within
the API.  The TicTacToe API can be played in either single or two player mode.

##Scoring##
Formula for scoring a game is:<br>
wins + (draws * .5)\ (total games)

##API Methods##

###*create_user*###
_Description:_ <br>
Function allows users to be created in the User data store for playing Tic-Tac-Toe.  Only requirement is that the user name "\<Computer>" is a reserved player for single player games.  A request to create that user name will trigger an exception.<br>
_Inputs:_<br>
user_name (String) Required Description: Desired user_name you wish to have<br>
email (String) Required Description: Valid email address<br>
_Output_:<br>
message (String) Description: Response message confirming user was created.

###*new_game*###
_Description:_<br>
Creates a new TicTacToe game in the Game data store.  This can be a one or two player game.  If no second player is assigned moves will be randomly generated on the second turn.<br>
_Inputs:_<br>
user_name1 (String) Required Description: Valid user name from data store User.<br>
user_name2 (String) Description: Valid user name from data store User.<br>
_Output:_<br>
message (String) Description: Response message confirming game was created.

###*get_user_rankings*###
_Description:_<br>
Returns a list of user ranked by the user with the highest winning percentage calculated by:<br>
wins + (draws * .5)\ (total games).  In the event of a tie the user with the least amount<br>
of total moves will be used as a tiebreaker.<br>
_Inputs:_<br>
num_results (Integer) Description: Number from 1:n will fetch the requested number of rankings.<br>
If left blank function will return all the results.<br>
_Output:_<br>
message (String) Description: Response message listing the user rankings showing the user name,<br>
win percentage, and the number of moves.

###*get_game_history*###
_Description:_<br>
Returns a list of moves made during a user provided game.  The output is the user, position, if game is a draw and if game is over.<br>
_Inputs:_<br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
_Output:_<br>
message (String) Description: Response message listing the game history of moves for that game.

###*cancel_game*###
_Description:_<br>
Cancels active game the specified user is player.  If authorized the Game and GameHistory objects will be deleted from the data  store<br>
_Inputs:_<br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
user (String) Required Description: Username requesting to cancel game.<br>
_Output:_<br>
message (String) Description: Response message confirming game has been deleted.

###*get_user_games*###
_Description:_<br>
Gets a list of all active games for the user provided.<br>
_Inputs:_<br>
user (String) Required Description: Username requesting active games.<br>
_Output:_<br>
message (String) Description: Response message listing active games by game id.

###*get_game*###
_Description:_<br>
Return the current state of a requested game.<br>
_Inputs:_<br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
_Output:_<br>
message (String) Description: Response message listing current state of game.

###*make_move*###
_Description:_<br>
Updates the Game grid with the position the player requests.  If the position is already occupied or it isn't the requested players turn the update to the grid will not take place and a message will notify the user that their move was unsuccessful.  If the Game is a single player game the computer will make a randomly generated move after the user makes their move and the game hasn't ended.   If the move is successful the procedure will check if the user has won the game or if there are no more moves remaining the game will result in a draw.  Successful moves will also write results in the GameHistory and moves that end the game will record entries in the Score object in the data store.<br>
_Inputs:_<br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
player (String) Required Description: Player making move.<br>
pos (Integer) Required Range: 0-8 Description: Position where user is making move.<br>
_Output:_<br>
message (String) Description: Response message listing if the move was successful.
