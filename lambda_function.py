import io
import random
import chess
import chess.pgn
import chess.engine

import boto3
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('chess')

# Copy engine to temp and set permissions to 755
import os, sys, stat, shutil
shutil.copyfile("./stockfish_20011801_x64", "/tmp/stockfish_20011801_x64")
os.chmod('/tmp/stockfish_20011801_x64', 0o755)
engine = chess.engine.SimpleEngine.popen_uci("/tmp/stockfish_20011801_x64")

# Globals
userId = False
board = False

# Static Speech
thanks_talk = "This skill has benefited greatly from the use of open source software and creative commons media. We specifically acknowledge, with thanks, the producers of the following."
python_talk = "The python-chess library, licensed under GPL 3."
engine_talk = "The Stockfish Open Source Chess Engine, licensed under GPL 3."
author_talk = "Johann Sebastian Bach's Sinfonias where played on the piano by Randolph Hokanson, licensed under Creative Commons Attribution-Share Alike 2.0."
acknowledgement = '{} {} {} {}'.format(thanks_talk, python_talk, engine_talk, author_talk)

hello_help = "Welcome to Blindfold Chess, by laynr!"
intro_help = 'Blindfold chess (also known as sans voir) is a form of chess play where the players do not see or touch the pieces. This forces players to maintain a mental model of the positions of the pieces.'
board_help = "Each square of the chessboard is identified by a unique coordinate pair of a letter and a number. The vertical columns of squares are labeled A. through H. from White's left to right. The horizontal rows of squares are numbered 1 to 8 starting from White's side of the board. Thus, each square has a unique identification of a letter followed by a number. For example, White's king starts the game on square E1, and Black's knight on B8."
moves_help = "Moves are communicated via the recognized Universal Chess notation.  This is done by first saying the cordinates of where the piece currently is, followed by the cordinates of where you want to move the piece. For example, Black's knight on B8 can move to open square A6 by saying, 'Alexa, move B8 to A6'."
castle_mov = "To castle indicate the final position of the King. For example, for white to castle kingside say, 'Alexa, move E1 to G1'."
En_passant = "Similarly, to en passant, indicate the final position of the pawn."
promotions = "If the Pawn reaches the opposite side of the chessboard, it will automatically be promoted to a Queen. For example, to promote a pawn to a queen say, 'Alexa, move A7 to A8'."
moves_help = '{} {} {}'.format(moves_help, castle_mov, En_passant, promotions)
music_help = "Do not worry if this blindfold chess skill closes before you have made your move, the state of the game is saved and you can resume the game at any time by saying, 'Alexa, open blindfold chess'."
games_help = "A new game can be started at anytime by saying, 'Alexa, start a new game'. You will then be asked what skill level you want your computer apponent to be. Level one is the easiest and level twenty is the hardest. Finally, you will be asked if you want to be 'black' or 'white'.  According to the rules of chess, the player who moves the first piece is referred to as ’white', and the player who moves the second piece is referred to as 'black'."
helps_help = "You can hear these instructions again at any time by saying, 'Alexa, help'."
thank_help = "You can hear software and meadia acknowledgements at any time by saying, Alexa, list acknowledgements."
speech_help = "{} {} {} {} {} {} {} {}".format(hello_help, intro_help, board_help, moves_help, music_help, games_help, helps_help, thank_help)


letter_dictionary = {
    "a" :   "alpha",
    "b" :   "bravo",
    "c" :   "charlie",
    "d" :   "delta",
    "e" :   "echo",
    "f" :   "foxtrot",
    "g" :   "golf",
    "h" :   "hotel"
}

##############################
# Chess Functions
##############################

def create_pgn(board, white, black, skill_level):
    game = chess.pgn.Game.from_board(board)
    game.headers["Event"] = "Blindfold Chess"
    game.headers["Site"]  = "Alexa"
    game.headers["Date"]  = "todo: get date"
    game.headers["Round"] = "todo: count game number"
    game.headers["White"] = white
    game.headers["Black"] = black
    game.headers["SkillLevel"] = skill_level

    pgn = str(game)
    return pgn

def save_pgn(userId, pgn):
    table.put_item(
        Item={
                'userId': userId,
                'pgn': pgn
            }
    )

def save_game_state(board, white, black, skill_level):
    print('save_game_state')
    pgn = create_pgn(board, white, black, skill_level)
    save_pgn(userId, pgn)

def get_pgn(userId):
    print('get_pgn')
    result = table.get_item(
        Key={
                'userId': userId
            }
    )
    if 'Item' in result:
        pgn = result['Item']['pgn']
    else:
        pgn = False

    return pgn

def get_board(pgn):
    print('get_board')
    pgn = io.StringIO(pgn)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    return board

def get_card_content():
    pgn = get_pgn(userId)
    pgn = io.StringIO(pgn)
    game = chess.pgn.read_game(pgn)
    return str(game.mainline_moves())

def computer_move(skill_level):
    print('computer_move')
    skill_level = int(skill_level)
    engine.configure({"Skill Level": skill_level})
    result = engine.play(board, chess.engine.Limit(time=0.1))
    return result.move.uci()

def legal_move_commentary(uci):
    print('legal_move_commentary')
    expanded = '{} {} {} {}'.format(letter_dictionary[uci[0]], uci[1], letter_dictionary[uci[2]] ,uci[3])
    return expanded

def not_legal_move_commentary(from_coordinate, to_coordinate):
    print('not_legal_move_commentary')
    commentary = ''
    commentary += 'illegal move, '
    commentary += "can not move from {} to {}. Please try again, It is {}'s turn. Where do you want to move {}?".format(str(from_coordinate).upper(), str(to_coordinate).upper(), who(board.turn), who(board.turn))
    return commentary

def is_uci_move_legal(uci):
    global board
    legal_uci_moves = [move.uci() for move in board.legal_moves]
    return uci in legal_uci_moves

def get_music():
    number = str(random.randint(1,15)).rjust(2, "0")
    music = "<audio src='https://blindfold-chess.s3.amazonaws.com/Bach_Sinfonien{}.mp3'/>".format(number)
    return music

def who(player):
    return "White" if player == chess.WHITE else "Black"

def is_game_over_commentary():
    print('is_game_over_commentary')
    commentary = ''

    if board.is_checkmate():
        commentary = "Game ends in checkmate. " + who(not board.turn) + " wins!"
    elif board.is_stalemate():
        commentary = "Game ends in draw due to stalemate."
    elif board.is_fivefold_repetition():
        commentary = "Game ends in draw due to 5-fold repetition."
    elif board.is_insufficient_material():
        commentary = "Game ends in draw due to insufficient material."

    print(commentary)
    commentary += 'Say, "Alexa, start new game", to play again!'
    return commentary    

def answer_move(from_coordinate, to_coordinate):
    print('answer_move')
    global board
    pgn = get_pgn(userId)
    pgn = io.StringIO(pgn)
    game = chess.pgn.read_game(pgn)
    white = game.headers["White"]
    black = game.headers["Black"]
    skill_level = game.headers["SkillLevel"]

    commentary = ''

    uci = '{}{}'.format(from_coordinate, to_coordinate)

    if is_uci_move_legal(uci):
        user_move_commentary     = 'okay, {} moves {}.'.format(who(board.turn), legal_move_commentary(uci))
        print('{} moves: {}'.format(who(board.turn), legal_move_commentary(uci)))
        #board.push_uci(uci)
        move = board.find_move((getattr(chess, from_coordinate.upper())), (getattr(chess, to_coordinate.upper())))
        if move.promotion:
            user_move_commentary += ' defaulting to queen promotion'
            print('defaulting to queen promotion')
        board.push(move)
        save_game_state(board, white, black, skill_level)
        if board.is_game_over():
            commentary = is_game_over_commentary()
            return commentary

        uci = computer_move(skill_level)
        computer_move_commentary = 'And now {} moves {}. '.format(who(board.turn),legal_move_commentary(uci))
        print('{} moves: {}'.format(who(board.turn), legal_move_commentary(uci)))
        board.push_uci(uci)
        save_game_state(board, white, black, skill_level)
        if board.is_game_over():
            commentary = is_game_over_commentary()
            return commentary

        prompt = "It is {}'s turn. Where do you want to move {}?".format(who(board.turn),who(board.turn))

        commentary += '{} {} {}'.format(user_move_commentary, computer_move_commentary, prompt)

    else:
        if board.is_game_over():
            commentary = is_game_over_commentary()
            return commentary
        commentary += not_legal_move_commentary(from_coordinate, to_coordinate)

    return commentary

def answer_new_game(skill_level, player):
    print('answer_new_game')
    global board

    if 'black' == player:
        black = 'Human'
        white = 'Stockfish'
    if 'white' == player:
        white = 'Human'
        black = 'Stockfish'

    board = chess.Board()
    save_game_state(board, white, black, skill_level)
    commentary = 'Your new game is ready! '

    if 'black' == player:
        uci = computer_move(skill_level)
        commentary += '{} moves first and moves {}. '.format(who(board.turn),legal_move_commentary(uci))
        print('{} moves: {}'.format(who(board.turn), legal_move_commentary(uci)))
        board.push_uci(uci)
        save_game_state(board, white, black, skill_level)
         
    music = get_music()
    commentary += "It is {}'s turn. Where do you want to move {}? {}".format(who(board.turn),who(board.turn), music)

    return commentary


##############################
# Response Builders
##############################

def build_speechlet_response(card_title, card_content, speech_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + speech_output + "</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': card_title,
            'content': card_content
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + reprompt_text + "</speak>"
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(speechlet_response, session_attributes={}):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


##############################
# Slot Handlers
##############################

def get_slot_id(slots, slot_name):
    print('get_slot_id slots={} AND slot_name={} '.format(slots, slot_name))

    slot_id = False
    if slots:
        if slots.get(slot_name, False):
            if slots[slot_name].get('resolutions', False):
                try:
                    slot_id = slots[slot_name]['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
                except KeyError:
                    try:
                        slot_id = slots[slot_name]['resolutions']['resolutionsPerAuthority'][1]['values'][0]['value']['id']
                    except KeyError:
                        slot_id = False
            else:
                slot_id = slots[slot_name].get('value', False)

    print('{} = {}'.format(slot_name, slot_id))
    return slot_id


##############################
# Intent Handlers
##############################

# Custom Intents
def new_game_intent(intent):
    print('new_game_intent')
    global board

    slots = intent.get('slots', False)
    skill_level = get_slot_id(slots, 'level')
    player      = get_slot_id(slots, 'player')

    if player != 'white':
        if player != 'black':
            player = False
    try:
        if not 0 <= int(skill_level) <= 20:
            skill_level = False
    except ValueError:
        skill_level = False

    if skill_level and player:
        card_title = 'Blindfold Chess Score Sheet'
        card_content = get_card_content()
        speech_output = answer_new_game(skill_level, player)
        reprompt_text = "Your game has been saved, say Alexa open blindfold chess to resume your game at any time.  It is {}'s turn. Where do you want to move {}?".format(who(board.turn),who(board.turn))
    else:
        card_title = 'Error creating new game'
        card_content = "I did not understand your new game request. You must choose a level between 1 and 20 and choose to be black or white. What would you like to do now?"
        speech_output = "I did not understand your new game request. You must choose a level between 1 and 20 and choose to be black or white. What would you like to do now?"
        reprompt_text = "What would you like to do now?"
    
    return build_response(
        build_speechlet_response(
            card_title = card_title,
            card_content = card_content,
            speech_output = speech_output,
            reprompt_text = reprompt_text,
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )

def move_intent(intent):
    print('move_intent')
    global board

    slots = intent.get('slots', False)
    from_coordinate   = get_slot_id(slots, 'from_coordinate')
    to_coordinate = get_slot_id(slots, 'to_coordinate')

    if from_coordinate and to_coordinate:
        responce = answer_move(from_coordinate, to_coordinate)
    else:
        responce = "I did not understand your move. Instead of letters try using; alpha, bravo, charlie, delta, echo, foxtrot, golf, or hotel. It is {}'s turn. Where do you want to move {}?".format(who(board.turn),who(board.turn))

    music = get_music()
    card_content = get_card_content()

    return build_response(
        build_speechlet_response(
            card_title = 'Blindfold Chess Score Sheet',
            card_content = card_content,
            speech_output = '{} {}'.format(responce, music),
            reprompt_text = "Your game has been saved, say Alexa open blindfold chess to resume your game at any time.  It is {}'s turn. Where do you want to move {}?".format(who(board.turn),who(board.turn)),
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )

def acknowledgement_intent(intent):
    print('acknowledgement_intent')
    global board

    if board == False:
        # Create new game
        board = chess.Board()
        save_game_state(board, 'Human', 'Stockfish', '1')


    card_content = acknowledgement
    reprompt_text = "It is {}'s turn. Where do you want to move {}?".format(who(board.turn),who(board.turn))
    speech_output = '{} {}'.format(card_content, reprompt_text)

    return build_response(
        build_speechlet_response(
            card_title = 'Blindfold Chess Acknowledgements',
            card_content = card_content,
            speech_output = speech_output,
            reprompt_text = reprompt_text,
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )

# Required Intents
def help_intent(intent):
    print('help_intent')
    content = "Sorry, your voice command was not recognized.  Please try again. What do you want to do?"
    return build_response(
        build_speechlet_response(
            card_title = "Voice command not recognized.",
            card_content = content,
            speech_output = content,
            reprompt_text = "You can Say 'start a new game', or move a piece by saying the cordinates of where the piece currently is, followed by the cordinates of where you want the piece to go to.  Or if you need help say, 'Alexa, help'.  What do you want to do?",
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )

def fallback_intent(intent):
    print('fallback_intent')
    content = '{} What do you want to do?'.format(speech_help)
    return build_response(
        build_speechlet_response(
            card_title = "Full Directions",
            card_content = content,
            speech_output = content,
            reprompt_text = 'Say "start a new game", or move a piece by saying the cordinates of where the piece currently is, followed by the cordinates of where you want the piece to go to.  What do you want to do?',
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )

def end_intent(intent):
    print("end_intent")
    return build_response(build_speechlet_response(card_title='Good Bye',card_content='',speech_output='Your game has been saved, say Alexa open blindfold chess to resume your game at any time.  Good Bye',reprompt_text='', should_end_session = True))


##############################
# Request Handlers
##############################

def log_request(request):
    locale        = request['locale']
    timestamp     = request['timestamp']
    requestId     = request['requestId']
    requestType   = request['type']
    return ('locale:{}\ntimestamp:{}\nrequestId:{}\nrequestType:{}'.format(locale,timestamp,requestId,requestType))

def on_launch(request):
    print ('on_launch')
    print (log_request(request))
    global board
    responce = ''
    
    if board:
        # Load previous game
        responce += 'Welcome back! '
        responce += 'Previous game loaded. '
        if board.is_game_over():
            responce += is_game_over_commentary()
    else:
        # Create new game
        responce += speech_help
        board = chess.Board()
        save_game_state(board, 'Human', 'Stockfish', '1')
        music = get_music()
        responce += "It is {}'s turn. Where do you want to move {}? {}".format(who(board.turn),who(board.turn),music)

    card_content = get_card_content()

    return build_response(
        build_speechlet_response(
            card_title = 'Blindfold Chess Score Sheet',
            card_content = card_content,
            speech_output = responce,
            reprompt_text = 'Say where you want to move, or say start a new game, or ask for help. What do you want to do?',
            should_end_session = False
        ),
        session_attributes = {'a':'apple'}
    )


def on_intent(request):
    """Dispatch to your skill's intent handlers"""
    print('on_intent')
    print(log_request(request))

    intent = request['intent']
    intentName = request['intent']['name']
    print(intentName)

    # Custom Intents
    if intentName == "AcknowledgementIntent":
        return acknowledgement_intent(intent)

    if intentName == "NewGameIntent":
        return new_game_intent(intent)

    if intentName == "MoveIntent":
        return move_intent(intent)

    # Required Intents
    if intentName == 'AMAZON.FallbackIntent':
        return fallback_intent(intent)

    if intentName == "AMAZON.HelpIntent":
        return help_intent(intent)

    if intentName == "AMAZON.CancelIntent":
        return end_intent(intent)

    if intentName == "AMAZON.StopIntent":
        return end_intent(intent)   

    raise ValueError('Invalid Intent Name: {}'.format(intentName))


##############################
# Session Handlers
##############################

def on_session_start(session):
    """ Called when a new session starts """
    print('on_session_start')
    global board
    global userId
    
    userId        = session['user']['userId']
    sessionId     = session['sessionId']
    applicationId = session['application']['applicationId']
    print('userId:{}\nsessionId:{}\napplicationId:{}'.format(userId,sessionId,applicationId))

    # Check if the user has an existing game is in the database 
    pgn = get_pgn(userId)
    if pgn:
        board = get_board(pgn)
    else:
        board = False

    return 

def on_session_ended(session):
    print("on_session_ended")
    return build_response(build_speechlet_response(card_title='Good Bye',card_content='',speech_output='Your game has been saved, say Alexa open blindfold chess to resume your game at any time.  Good Bye',reprompt_text='', should_end_session = True))


##############################
# Event Handler
##############################

def lambda_handler(event, context):
    """ Entry Point: First function to execute
    Documentation: https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html
    Parameters:
        event: AWS Lambda uses this parameter to pass in event data to the handler. Dict type.
        context: AWS Lambda uses this parameter to provide runtime information to your handler. LambdaContext type.
            Context Documentation: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Determine the type of request and handle appropriately
    The Alexa service sends your service a request using one of the standard request types when users engage with your skill by voice. There are three request types:
         LaunchRequest: Sent when the user invokes your skill without providing a specific intent.
         IntentRequest: Sent when the user makes a request that corresponds to one of the intents defined in your intent schema.
         SessionEndedRequest: Sent when the current skill session ends for any reason other than your code closing the session.
    Documentation: https://developer.amazon.com/docs/custom-skills/request-types-reference.html
    """

    # Only let your skill's applicatin ID talk to this lambda fuction. Add your amzn1.ask.skill to this test 
    #applicationId = event['session']['application']['applicationId']
    #if applicationId != "amzn1.ask.skill.f6791e32-cca6-442e-8346-7b5bed9a8911":
    #    raise ValueError('Invalid Application ID: {}'.format(applicationId))


    if event['request']['type'] == "LaunchRequest":
        if event['session']['new']:
            on_session_start(event['session'])        
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        if event['session']['new']:
            on_session_start(event['session']) 
        return on_intent(event['request'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['session'])