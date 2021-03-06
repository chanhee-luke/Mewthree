# Mewthree  ![mewthree](https://vignette.wikia.nocookie.net/pokemon/images/3/3b/Mewthree_manga.png/revision/latest?cb=20130407033659)
Mewthree is a Pokémon Showdown battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

This project is forked from https://github.com/pmariglia/showdown.

This bot is assuming we're doing random battles in generation 5.

This bot has a Makefile, where you must run `make install` and then `make test` to run the bot. `make clean` will remove the virtual environment installed.

## Milestone 2 & 3 & 4 & 5 & final(04/29)

### Overview of the bot

- Control mechnism: We use behavior tree as the main control mechanism of our bot
- High-level strategy: The bot is based on the maximin strategy. The bot first decides if it needs to attack or switch, then builds the tree for either attacking or switching. The bot currently searches for only depth 1 and does not account the opponents moves. This is a future work we will implement later in the milestone. 
- Implemented functionality: The bot is fully functional and will finish matches. There are a few edge cases such as all pokemons are out of move points (pp) that the bot fails to forfeit, since our bot isn't designed to forfeit and let the timer run out. We did not think this was a error that needs to be caught because once all pokemons are out of pp we lose anyways and is a very rare case. 

### For Milestone 3

For this milestone the bot searchs beyond the current game state to future game states upto depth 3. This enables the bot to function more intelligently by guessing the opponent's moves and acting accordingly. Still the bot makes the decision based on the min_max strategy by picking the move that is "safest" i.e. minimizing the potential loss.

### For Milestone 4

In this latest update, the bot has been given some new features in order to improve its Pokemon selection against the opponent. We included a make_best_order() which ranks the user's pokemons based on their damage compared to the enemy team. It returns a list of pokemons which has been sorted by their efficiencies. It compares each of the bot's Pokemons with that of the opponent. In order to do this, there is an additional funciton pokemonEfficiency() to calculate their efficiency based on their stats.

### For Milestone 5

In this update, we're finalizing our feature set. First, we added new chat features that happen from specific circumstances in the game. For example, we check if we have 3 more Pokemon than the opponent, and we then decide to chat and suggest that we are the ones playing against a bot. It doesn't really affect performance of the bot, but it was a fun feature that we had wanted. This was done in run_battle.py, and any chat implementation can be further added there.

The next feature we implemented was deciding if the bot will be aggressive or be defensive. Using HP as a metric, we made the bot more aggressive when behind and be more defensive when ahead. Aggressive moves are defined as a high-risk, high-return moves and defensive moves are defined as low-risk, low-return moves. We believe taking more aggressive approach when behind will enable us to beat the opponent better. 

Some ways to improve the bot is to take account of the opponent’s actions when creating the game which we will implement in the final project. Currently we don’t have any magic variables because everything is automated because the bot currently follows the following logic:

1. Checks who is winning by calculating HPs for both sides
2. Create the game tree (depth=2) by assuming opponent picks safest moves
3. Pick aggressive moves if the bot is losing, picking defensive move if the bot is winning

We will add magic variable for our final project that consists of 1) The game tree depth 2) Bot aggressiveness level.
The bot aggressiveness level is left to our final project because it needs to be tweaked together with the game tree depth to be effective because the current game tree only assumes the opponent will pick the defensive moves. By incorporating opponent’s previous moves when building the game tree we intend to make the bot more adaptable in our final project. 

### Final Update

For outstanding bugs, there are a lot of unknown moves, sets, and general errors from the forked bot. Unfortunately, these are not errors we can fix very well, unless we go into the dictionary files and find information manually ourselves. A lot of these bugs stem from the engine. One example is the Other than that, our bot still runs to completion, although some moves are still very questionable such as trying to constantly use a move that cannot affect the opponent.

For unimplemented features, we currently assume the opponent is going to make their safest move when ahead and aggressive move when behind. In the future, we would like to predict them to play more aggressively, defensively, etc. This would hopefully improve our winrate and elo gain. Furthermore, the bot could build a deeper search tree but currently we limit ourselves to depth 3 to lessen decision making time. We also only can play a single game on the Gen5 Random Battle.

We didn't get to implement any machine learning bot. This proved to be out of scope for our project as we decided to iteratively improve our one bot.

### For Future Contributors
All bots are under `showdown/battle_bots/` and all bots should be structured as an object inheriting the Battle class. The only method that is called by the websocket is the `find_best_move()` method and its the minimum method one needs to implement in order to make the bot functional. Check `battle.py` under `showdown/` to see what methods and attributes the Battle class has. 

### Dependencies

No dependency for the game (web-based game)

For the bot:
- python==3.6.3
- requests==2.20.1
- environs==4.1.0
- websockets==7.0
- python-dateutil==2.8.0
- nashpy==0.0.17
- pandas==0.23.4
- numpy==1.16.2

### Install Dependencies

`make install`

Performs pip install of all requirements

### Set up Runtime Environment and Running the Bot

`make build`

Creates a Python virtualenv and runs the bot

### Running/Testing the Bot

0. Check if dependencies are all installed
1. Create an acount on the [pokemonshowdown.com](https://pokemonshowdown.com) website
2. Edit the .env file on the repository and set `PS_USERNAME` and `PS_PASSWORD` to the created username and password
3. Log in to the game website
4. Run `make build` and see the bot starting the game doing your job!


# Everything below is PMariglia's ReadMe on the Engine:

The bot can play single battles in generations 4 through 8 however some of the battle mechanics assume it is gen8.

![badge](https://action-badges.now.sh/pmariglia/showdown)

## Python version
Developed and tested using Python 3.6.3.

## Getting Started


### Configuration
Environment variables are used for configuration which are by default read from a file named `.env`

The configurations available are:
```
BATTLE_BOT: (string, default "safest") The BattleBot module to use. More on this below
SAVE_REPLAY: (bool, default False) Specifies whether or not to save replays of the battles
LOG_LEVEL: (string, default "DEBUG") The Python logging level 
WEBSOCKET_URI: (string, default is the official PokemonShowdown websocket address: "sim.smogon.com:8000") The address to use to connect to the Pokemon Showdown websocket 
PS_USERNAME: (string, required) Pokemon Showdown username
PS_PASSWORD: (string) Pokemon Showdown password 
BOT_MODE: (string, required) The mode the the bot will operate in. Options are "CHALLENGE_USER", "SEARCH_LADDER", or "ACCEPT_CHALLENGE"
USER_TO_CHALLENGE: (string, required if BOT_MODE is "CHALLENGE_USER") The user to challenge
POKEMON_MODE: (string, required) The type of game this bot will play games in
TEAM_NAME: (string, required if POKEMON_MODE is one where a team is required) The name of the file that contains the team you want to use. More on this below in the Specifying Teams section.
RUN_COUNT: (integer, required) The amount of games this bot will play before quitting
```

Here is a minimal `.env` file. This configuration will log in and search for a gen8randombattle:
```
WEBSOCKET_URI=sim.smogon.com:8000
PS_USERNAME=MyCoolUsername
PS_PASSWORD=MySuperSecretPassword
BOT_MODE=SEARCH_LADDER
POKEMON_MODE=gen8randombattle
RUN_COUNT=1
```

### Running without Docker

#### Clone

Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

#### Install Requirements

Install the requirements with `pip install -r requirements.txt`.

Be sure to use a virtual environment to isolate your packages.

#### Run
Running with `python run.py` will start the bot with configurations specified by environment variables read from a file named `.env`

### Running with Docker

#### Clone the repository
`git clone https://github.com/pmariglia/showdown.git`

#### Build the Docker image
`docker build . -t showdown`

#### Run with an environment variable file
`docker run --env-file .env showdown`

### Running on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

After deploying, go to the Resources tab and turn on the worker.

## Battle Bots

### Safest
use `BATTLE_BOT=safest` (default unless otherwise specified)

The bot searches through the game-tree for two turns and selects the move that minimizes the possible loss for a turn.
This is equivalent to the [Maximin](https://en.wikipedia.org/wiki/Minimax#Maximin) strategy

For decisions with random outcomes a weighted average is taken for all possible end states.
For example: If using draco meteor versus some arbitrary other move results in a score of 1000 if it hits (90%) and a score of 900 if it misses (10%), the overall score for using
draco meteor is (0.9 * 1000) + (0.1 * 900) = 990.

This decision type is deterministic - the bot will always make the same move given the same situation again.

### Nash-Equilibrium (experimental)
use `BATTLE_BOT=nash_equilibrium`

Using the information it has, plus some assumptions about the opponent, the bot will attempt to calculate the [Nash-Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium) with the highest payoff
and select a move from that distribution.

The Nash Equilibrium is calculated using command-line tools provided by the [Gambit](http://www.gambit-project.org/) project.
This decision method should only be used when running with Docker and will fail otherwise.

This decision method is **not** deterministic. The bot **may** make a different move if presented with the same situation again.

### Most Damage
use `BATTLE_BOT=most_damage`

Selects the move that will do the most damage to the opponent

Does not switch

## Performance

These are the default battle-bot's results in three different formats for roughly 75 games played on a fresh account:

![RelativeWeightsRankings](https://i.imgur.com/eNpIlVg.png)

## Write your own bot
Create a package in `showdown/battle_bots` with a module named `main.py`. In this module, create a class named `BattleBot`, override the Battle class, and implement your own `find_best_move` function.

Set the `BATTLE_BOT` environment variable to the name of your package and your function will be called each time PokemonShowdown prompts the bot for a move

## The Battle Engine
The bots in the project all use a Pokemon battle engine to determine all possible transpositions that may occur from a pair of moves.

For more information, see [ENGINE.md](https://github.com/pmariglia/showdown/blob/master/ENGINE.md) 

## Specifying Teams
You can specify teams by setting the `TEAM_NAME` environment variable.
Examples can be found in `teams/teams/`.

Passing in a directory will cause a random team to be selected from that directory

The path specified should be relative to `teams/teams/`.

#### Examples

Specify a file:
```
TEAM_NAME=gen8/ou/clef_sand
```

Specify a directory:
```
TEAM_NAME=gen8/ou
```
