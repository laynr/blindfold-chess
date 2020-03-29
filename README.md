# blindfold chess

## Introduction
This is an Amazon Alexa skill that allows you to play chess against a computer competitor (Stockfish) with out the aid of a chess board. Blindfold chess (also known as sans voir) is a form of chess play where the players do not see or touch the pieces. This forces players to maintain a mental model of the positions of the pieces.

## Installation
You can install blindfold-chess on any Alexa enabled device by saying, "Alexa, install blindfold chess".  
Or by visiting https://www.amazon.com/Laynr-blindfold-chess/dp/B0859QF8YL 

You can then play blindfold chess by saying, "Alexa, open blindfold chess"

## Build

```bash
pip install --target ./package python-chess
cd package
zip -r9 ../function.zip .
cd ..
zip -g function.zip lambda_function.py
zip -g function.zip stockfish_20011801_x64  <-- download latests Stockfish for Linux at https://stockfishchess.org/download/ 
```
### Code:
Upload 'function.zip' to https://console.aws.amazon.com/lambda
Upload 'Interaction-Model.json' to https://developer.amazon.com/alexa/console/ask

### Database:
Create 'chess' database table at https://console.aws.amazon.com/dynamodb/home

### Media:
Create 'blindfold-chess' bucket for media at https://s3.console.aws.amazon.com/s3/home
Music files have been downloaded from: https://en.wikipedia.org/wiki/Inventions_and_Sinfonias_(Bach)
Converted from ogg to mp3 with ffmpeg: ffmpeg -i Bach_Sinfonien16.ogg -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0 Bach_Sinfonien16.mp3
Hosted at: https://blindfold-chess.s3.amazonaws.com/Bach_Sinfonien01.mp3

## Usage
"Alexa, open blindfold chess"

Each square of the chessboard is identified by a unique coordinate pair of a letter and a number. The vertical columns of squares are labeled A. through H. from White's left to right. The horizontal rows of squares are numbered 1 to 8 starting from White's side of the board. Thus, each square has a unique identification of a letter followed by a number. For example, White's king starts the game on square E1, and Black's knight on B8.

Moves are communicated via the recognized Universal Chess notation. This is done by first saying the cordinates of where the piece currently is, followed by the cordinates of where you want to move the piece. For example, Black's knight on B8 can move to open square A6 by saying, 'Alexa, move B8 to A6'. To castle indicate the final position of the King. For example, for white to castle kingside say, 'Alexa, move E1 to G1'. Similarly, to en passant, indicate the final position of the pawn.

A new game can be started at anytime by saying, 'Alexa, start a new game'. You will then be asked what skill level you want your computer apponent to be. Level one is the easiest and level twenty is the hardest. Finally, you will be asked if you want to be 'black' or 'white'. According to the rules of chess, the player who moves the first piece is referred to as white', and the player who moves the second piece is referred to as 'black'.

Do not worry if this blindfold chess skill closes before you have made your move, the state of the game is saved and you can resume the game at any time by saying, 'Alexa, open blindfold chess'.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Acknowledgements
This skill has benefited greatly from the use of open source software and creative commons media. We specifically acknowledge, with thanks, the producers of the following:

The python-chess library, licensed under GPL 3. 

The Stockfish Open Source Chess Engine, licensed under GPL 3. 

Johann Sebastian Bach's Sinfonias where played on the piano by Randolph Hokanson, licensed under Creative Commons Attribution-Share Alike 2.0.

## License
blindfold-chess is licensed under the GPL 3 (or any later version at your option). Check out LICENSE.txt for the full text.