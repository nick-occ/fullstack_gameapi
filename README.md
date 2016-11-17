#TicTacToe API#

##Description##
This API will allow developers to develop a front-end TicTacToe application by accessing functions created within
the API.  The TicTacToe API can be played in either single or two player mode.

##API Methods##

###*create_user*###
_Description:_ <br>
Function allows user to be created in games data store User.<br>
_Inputs:_<br>
user_name (String) Required Description: Desired user_name you wish to have<br>
email (String) Required Description: Valid email address<br>
_Output_:<br>
message (String) Description: Response message confirming user was created.


###*new_game*###
_Description:_<br>
Creates a new TicTacToe game in data store Game.  This can be a one or two player game.  If no second player is assigned moves will be randomly generated on the second turn.<br>
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
