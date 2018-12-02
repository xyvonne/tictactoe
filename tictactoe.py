#! /usr/bin/env python3
# -*- coding: utf-8 -*-8

from random import random

##############################################################################
# Grid
##############################################################################

class Grid:
    '''
    Handle the grid.

    Attributes:
    * array: the grid layout -- a list of 9 ints. Indices refer to the
    following layout:

    -------
    |6|7|8|
    -------
    |3|4|5|
    -------
    |0|1|2|
    -------

    In this class, 'moves' also refer to this layout, and therefore range in
    [0;8].
    The values range in [0;2] with the following convention:
    0 = player 'X' (first player)
    1 = player 'O' (second player)
    2 = empty square (in this context, this number '2' is called 'EMPTY',
    for code readability)
    * plies: number of plies ("half-moves") made so far, in other words the
    number of occupied squares in the grid.
    '''

    EMPTY = 2 # a convenient notation for empty squares
    empty_array = 9 * [EMPTY] # array for the empty grid
    symbols = "XO." # replace 0 by 'X', 1 by 'O', and 2 (EMPTY) by '.'

    def __init__(self, array=empty_array):
        '''
        Constructor.
        Takes 1 optional parameter: the list (array) corresponding
        to the grid. If it is not specified, initialization is made with an
        empty grid.
        '''
        self.array = array
        self.plies = 9 - self.array.count(Grid.EMPTY)

    def __str__(self):
        '''
        Represent the grid (for pretty-printing purposes).
        '''
        s = ""
        for i in range(3):
            for j in range(3):
                s += Grid.symbols[self.array[6 - 3 * i + j]]
            s += '\n'
        return s

    def clear(self):
        '''
        Clear the grid.
        '''
        self.array = Grid.empty_array[:]
        self.plies = 0

    def play(self, move):
        '''
        If possible, put a mark ('O' or 'X') at location 'move'.
        Return 'True' or 'False' whether the move is valid or not.
        'move' must be in [0,...,8], it is the caller's duty to ensure this.
        '''
        assert move in range(9), "Move must be in [0,...,8]"
        if self.array[move] != Grid.EMPTY:
            return False
        self.array[move] = (self.plies % 2)
        self.plies += 1
        return True

    def undo(self, move):
        '''
        If possible, undo the move, i.e. free the occupied square refered
        by 'move'.
        Return 'True' or 'False' whether the square was occupied or not.
        'move' must be in [0,...,8], it is the caller's duty to ensure this.
        '''
        assert move in range(9), "Move must be in [0,...,8]"
        if self.array[move] == Grid.EMPTY:
            return False
        self.array[move] = Grid.EMPTY
        self.plies += -1
        return True

    def has_won(self, player):
        '''
        Return 'True' iff 'player' (0 for 'X', 1 for 'O')
        has just won the game.
        '''
        regions = [] # list of possible alignments
        regions.append([4 * i for i in range(3)]) # SW-NE diagonal
        regions.append([2 * i + 2 for i in range(3)]) # SE-NW diagonal
        for j in range(3):
            regions.append([3 * j + i for i in range(3)]) # horiz. alignments
            regions.append([3 * i + j for i in range(3)]) # vert. alignments

        # An auxiliary function: return 'True' iff 'player'
        # has his symbols in all squares of 'region'
        def has_them_all(region, player):
            for i in region:
                if self.array[i] != player:
                    return False
            return True

        # Test the win itself
        for region in regions:
            if has_them_all(region, player):
                return True
        return False

##############################################################################
# Game
##############################################################################

class Game:
    '''
    Handle the game execution.

    Attributes:
    * grid: the grid (an instance of Grid) corresponding to the current
    position.
    * ai: the AI engine (an instance of AI, see the Class AI below).
    * is_computer: a pair of Booleans (actually, of 0-1s), the first (resp.
    second) telling if 'X' (resp. 'O') is played by the computer or not.
    '''

    def __init__(self):
        '''
        Constructor.
        Create and empty grid, load the AI engine and configure the players
        using the 'select_players()' method.
        '''
        self.grid = Grid()
        self.ai = AI()
        self.select_players()

    def current_player(self):
        '''
        Return 0 if it's 'X''s turn, or 1 otherwise.
        '''
        return self.grid.plies % 2

    def select_players(self):
        '''
        Pop up a menu asking whether each player is a computer or not, and
        set the attribute 'is_computer' accordingly.
        '''
        print('\n' + 80 * '-')
        msg = "Choose game type:\n" \
                + "1:  player  vs player, 2:  player  vs computer,\n" + \
                "3: computer vs player, 4: computer vs computer\n"
        while True:
            try:
                answer = input(msg)
                answer = int(answer) - 1
                if answer < 0 or answer > 3:
                    raise ValueError
                break
            except ValueError:
                print("Invalid game type! Try again.")
        self.grid.clear()
        print('\n')
        print(self.grid)
        self.is_computer = answer // 2, answer % 2

    def player_move(self):
        '''
        Prompt the player for a move.
        [WARNING: a move is actually entered as a integer in 1-9
        (instead of 0-8), because this is more user-friendly: indeed,
        according to this new convention, the possible moves are given by
        the digit layout on a standard numpad.
        Remind anyway that the move is stored as an integer in 0-8 to comply
        with the Grid specifications.]
        Ensure that the entered move is valid, and if so, return it as an
        integer in 0-8.
        Do not actually play this move.
        '''
        player = Grid.symbols[self.current_player()]
        msg = "Player '{}', enter your move (1-9): ".format(player)
        while True:
            try:
                move = input(msg)
                move = int(move) - 1 # grid entries range in 0..8, not 1..9
                if move < 0 or move > 8 or self.grid.array[move] != Grid.EMPTY:
                    raise ValueError
                break
            except ValueError:
                print("Invalid move! Try again.")
        return move

    def computer_move(self):
        '''
        Assuming that it is computer's turn, compute the move it would play
        using the AI object, and return it as an integer in 0-8.
        Do not actually play this move.
        '''
        move = self.ai.evaluate(self.grid)[1]
        print("Computer (Player '{}') played {}!"
                .format(Grid.symbols[self.current_player()], str(move + 1)))
        return move

    def must_go_on(self):
        '''
        Return 'True' if the game is not over yet, 'False' otherwise.
        Draw and win for both players are tested, and messages are displayed
        accordingly.
        The case when both players aligned 3 of their symbols is not tested,
        as it cannot occur in practice.
        '''
        for player in range(2):
            if self.grid.has_won(player):
                print("Player '{}' wins!".format(Grid.symbols[player]))
                return False
        if self.grid.plies == 9:
            print("Draw game!")
            return False
        return True

    def play_a_game(self):
        '''
        Play a whole game once it is initialized
        (see the '__init__()' and 'select_players()' methods).
        Return the sequence of all played moves in order
        (here, moves are stored as integers in 1-9. This list is not
        used by this current version of the program, but it could be printed).
        '''
        moves = []
        while self.must_go_on():
            if self.is_computer[self.current_player()]:
                move = self.computer_move() # move is in 0-8
            else:
                move = self.player_move() # move is in 0-8
            self.grid.play(move)
            moves.append(move + 1) # by conv., all recorded moves range in 1-9
            print('\n')
            print(self.grid)
        return moves

    def wants_to_play_again(self):
        '''
        At the end of the game, ask if the user wants to play again,
        and return their answer as a Boolean
        ('True' for a positive answer, 'False' for a negative or invalid answ.)
        '''
        return input("Play again? ") in ("y", "Y", "yes", "Yes", "YES")

##############################################################################
# AI
##############################################################################

class AI:
    '''
    The AI engine for games with a computer.

    The derived algorithm is a MinMax; here, the amount of all
    possible games is very small, so the whole tree can be
    computed quickly. Thus, this AI plays perfectly. It solves the Tic-Tac-Toe
    game, with the following conclusions:
    - all possible first moves are good;
    - then, both players can secure the draw if they are smart enough, but
    neither can force a win. Computer vs computer games are thus always drawn.

    Attributes:
    * dict : this is the only attribute of this class. If it a dictionary
    whose keys are grid arrays (lists) converted to tuples (to be immutable),
    and values are pairs (evaluation, best_move).
    'evaluation' can take only 3 values: 1 if the position
    is (or leads to) a win for 'X', -1 for a win for 'O', and 0 for a draw.
    'best_move' is the move (in 0-8) the computer would play in this position
    if it were its turn. If the position is actually a game over, 'best_move'
    is by convention set to 0.
    '''

    def __init__(self):
        '''
        Constructor. Set the AI object with an empty dictionary.
        '''
        self.dict = {}

    def evaluate(self, grid):
        '''
        The very AI engine.
        It updates the dictionary for all evaluated (seen) positions, and
        returns the pair (evaluation, best_move) for the current position
        'grid'.
        Evaluation is straightforward for already evaluated games... or once
        it is already known (that is, the position is already in the
        dictionary).
        Otherwise, we derive the MinMax algorithm itself, going as far as
        possible -- that is, until we are left with a game over.
        Our implementation is based on
        recursive calls of the method 'evaluate' itself, with positions
        having more filled squares than the current one -- all of these
        positions are already evaluated, thanks to the induction hypothesis.
        Note that we can use 2 instead of 'math.inf' for infinity, because all
        evaluations range in -1..1.
        Note also that setting a sign 'sgn' to
        +1 if computer plays 'X'
        -1 if computer plays 'O',
        enables the factorization of the code of the 'max' and 'min'
        functions into only one function, because the conditions
        'best_val > val' (for 'max' update) and
        'best_val < val' (for 'min' update) are equivalent to
        '(best_val - val) * 'sgn > 0' (for both cases).
        Finally, when several equally good moves exist, we pick one at random,
        so that the computer answers can vary.
        '''
        d = self.dict
        key = tuple(grid.array)

        # If the game is over, or the grid is already evaluated, the
        # evaluation is straightforward.
        # For already ended games, we arbitrarily set the best move value to 0.
        if key in d:
            return d[key]
        for player in range(2):
            if grid.has_won(player):
                val = 1 - 2 * player # = 1 if player = 0 = 'X'; -1 otherwise
                d[key] = (val, 0)
                return d[key]
        if grid.plies == 9: # draw
            d[key] = (0, 0)
            return d[key]

        # If evaluation is not straightforward, we derive the MinMax algorithm
        # itself.
        # Note that we use a sign 'sgn' = +1 or -1 to handle min and max
        # simultaneously.
        sgn = 1 - 2 *(grid.plies % 2) # 1 if it's 'X''s turn; -1 otherwise
        inf = 2 # large enough value, as all evaluations are between -1 and 1
        best_val = - sgn * inf
        for move in (i for i in range(9) if grid.array[i] == Grid.EMPTY):
            grid.play(move)
            val = self.evaluate(grid)[0]
            if ((val - best_val) * sgn > 0) \
                    or ((val == best_val) and random() < .5):
                        # random() is used to not always play
                        # the same best move, if several exist
                best_val = val
                best_move = move
            grid.undo(move)
        d[key] = (best_val, best_move)
        return d[key]

##############################################################################
# Main
##############################################################################

def main():
    '''
    Play the game.
    '''
    while True:
        game = Game()
        game.play_a_game()
        if not(game.wants_to_play_again()):
            break
    del(game)
    print("\nGoodbye!")

if __name__ == '__main__':
    main()
