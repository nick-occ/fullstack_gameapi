#TicTacToe API

##Description
This API will allow developers to develop a front-end TicTacToe application by accessing functions created within
the API.  The TicTacToe API can be played in either single or two player mode.

##Scoring
Formula for scoring a game is:<br>
wins + (draws * .5)\ (total games)

As a tie break when ranking all the users the game also captures the number of moves it took the winner to make a move for each game and keeps a running total in the Score object.  In the event of a tie winning percentage, the user with the least amount of moves will be ranked higher.

##Rules of the Game
The Tic-Tac-Toe can be played in single or two player mode.  Player 1 starts out by making the first move in a 3x3 grid.  Once the move is made no future moves can be made in the same location.  Player 2 will then make a move in the Tic-Tac-Toe grid in a position that has not already been filled by a previous move.  The game will continue until either there are no more free spaces to make a move or one of the players has three consecutive areas filled matching either horizontally, vertically or diagonally.

##API URL
https://apis-explorer.appspot.com/apis-explorer/?base=https://gameapp-145818.appspot.com/_ah/api#p/tictactoe/v1/

##API Methods
###*create_user*
<b>_Path:_</b> 'user' <br>
<b>_Method:_</b> POST <br>
<b>_Parameters:_</b><br>
user_name (String) Required Description: Desired user_name you wish to have<br>
email (String) Required Description: Valid email address<br>
<b>_Returns:_</b><br>
message (String) Description: Response message confirming user was created.<br>
<b>_Description:_</b> <br>
Function allows users to be created in the User data store for playing Tic-Tac-Toe.  Only requirement is that the user name "\<Computer>" is a reserved player for single player games.  A request to create that user name will trigger an exception.<br>

###*new_game*
<b>_Path:_</b> 'game' <br>
<b>_Method:_</b> POST <br>
<b>_Parameters:_</b><br>
user_name1 (String) Required Description: Valid user name from data store User.<br>
user_name2 (String) Description: Valid user name from data store User.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message confirming game was created.</br>
<b>_Description:_</b> <br>
Creates a new TicTacToe game in the Game data store.  This can be a one or two player game.  If no second player is assigned moves will be randomly generated on the second turn.<br>

###*get_user_rankings*
<b>_Path:_</b> 'scores' <br>
<b>_Method:_</b> GET <br>
<b>_Parameters:_</b><br>
num_results (Integer) Description: Number from 1:n will fetch the requested number of rankings.<br>
If left blank function will return all the results.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message listing the user rankings showing the user name,<br>
win percentage, and the number of moves.<br>
<b>_Description:_</b><br>
Returns a list of user ranked by the user with the highest winning percentage calculated by:<br>
wins + (draws * .5)\ (total games).  In the event of a tie the user with the least amount<br>
of total moves will be used as a tiebreaker.<br>

###*get_game_history*
<b>_Path:_</b> 'history' <br>
<b>_Method:_</b> GET <br>
<b>_Parameters:_</b><br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message listing the game history of moves for that game.<br>
<b>_Description:_</b><br>
Returns a list of moves made during a user provided game.  The output is the user, position, if game is a draw and if game is over.<br>

###*cancel_game*
<b>_Path:_</b> 'game/{urlsafe_game_key}/cancel' <br>
<b>_Method:_</b> POST <br>
<b>_Parameters:_</b><br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
user (String) Required Description: Username requesting to cancel game.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message confirming game has been deleted.<br>
<b>_Description:_</b><br>
Cancels active game the specified user is player.  If authorized the Game and GameHistory objects will be deleted from the data  store<br>

###*get_user_games*
<b>_Path:_</b> 'games/{user}' <br>
<b>_Method:_</b> GET <br>
<b>_Parameters:_</b><br>
user (String) Required Description: Username requesting active games.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message listing active games by game urlsafe key.<br>
<b>_Description:_</b><br>
Gets a list of all active games for the user provided.<br>

###*get_game*
<b>_Path:_</b> 'game/{urlsafe_game_key}' <br>
<b>_Method:_</b> GET <br>
<b>_Parameters:_</b><br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message listing current state of game.<br>
<b>_Description:_</b><br>
Return the current state of a requested game.<br>

###*make_move*
<b>_Path:_</b> 'game/{urlsafe_game_key}' <br>
<b>_Method:_</b> POST <br>
<b>_Parameters:_</b><br>
urlsafe_game_key (String) Required Description: URL Safe Game Key of Game object in data store.<br>
player (String) Required Description: Player making move.<br>
pos (Integer) Required Range: 0-8 Description: Position where user is making move.<br>
<b>_Returns:_</b><br>
message (String) Description: Response message listing if the move was successful.<br>
<b>_Description:_</b><br>
Updates the Game grid with the position the player requests.  If the position is already occupied or it isn't the requested players turn the update to the grid will not take place and a message will notify the user that their move was unsuccessful.  If the Game is a single player game the computer will make a randomly generated move after the user makes their move and the game hasn't ended.   If the move is successful the procedure will check if the user has won the game or if there are no more moves remaining the game will result in a draw.  Successful moves will also write results in the GameHistory and moves that end the game will record entries in the Score object in the data store.<br>
