from game import Game
import sys
import os


def main():

    g = Game(sys.argv[1])
    g.run()


if __name__ == "__main__":
    main()
