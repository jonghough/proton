
import click
from games.piratedefense.piratedefensescene import PirateDefenseScene
from proton.protonengine import ProtonEngine
from games.othello.othelloscene import OthelloScene
from games.asteroiddodge.asteroidscene import AsteroidScene

@click.command() 
@click.option('--game', prompt='path to the game configuraiton file',
              help='The configuration (YAML) file defining the game parameters.')
def launch(game):
    engine = ProtonEngine(game) 
    engine.run()

if __name__ == "__main__": 
    launch()
     