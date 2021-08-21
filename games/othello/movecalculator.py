import math

from games.othello.squarecontroller import SquareController


class MoveCalculator(object):
    ''' Move calculator for determining which moves are possible.
    '''
    @staticmethod
    def can_find_same_color_along_line(board, x, y, xdir, ydir, max, colortomatch):
        success = False

        if xdir == 0:
            if ydir < 0:
                maxy = -1
            else:
                maxy = max
            for j in range(y + ydir, maxy, ydir):
                if board._squares[x * max + j] == colortomatch:
                    success = True
                    break
                elif board._squares[x * max + j] == SquareController.NONE:
                    success = False
                    break

        elif ydir == 0:
            if xdir < 0:
                maxx = -1
            else:
                maxx = max
            for i in range(x + xdir, maxx, xdir):
                if board._squares[i * max + y] == colortomatch:
                    success = True
                    break
                elif board._squares[i * max + y] == SquareController.NONE:
                    success = False
                    break
        else:
            if ydir < 0:
                maxy = -1
            else:
                maxy = max
            if xdir < 0:
                maxx = -1
            else:
                maxx = max
            for i,j in zip(range(x + xdir, maxx, xdir),range(y + ydir, maxy, ydir)):
                if board._squares[i * max + j] == colortomatch:
                    success = True
                    break
                elif board._squares[i * max + j] == SquareController.NONE:
                    success = False
                    break

        return success

    @staticmethod
    def can_make_move(board, x, y, max, currentcolor):
        canPut = False
        if x < 0 or x >= max or y < 0 or y >= max or currentcolor == SquareController.NONE:
            canPut = False

        elif board._squares[x * max + y] != SquareController.NONE:
            canPut = False
        else:
            enemycolor = -currentcolor
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    elif x + i >= 0 and x + i < max and y + j >= 0 and y + j < max:
                        if board._squares[(x + i) * max + (y + j)] == enemycolor:
                            if MoveCalculator.can_find_same_color_along_line(board, x, y, i, j, max, currentcolor):
                                return True

        return canPut

    @staticmethod
    def make_move(board, x, y, max, currentcolor):
        if x < 0 or x >= max or y >= max or currentcolor == SquareController.NONE:
            return
        board._squares[x * 8 + y] = currentcolor
        ok = False
        finish = False
        enemycolor = SquareController.WHITE
        if currentcolor == SquareController.WHITE:
            enemycolor = SquareController.BLACK

        for i, j in zip(range(x + 1, max), range(y + 1, max)):
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for i, j in zip(range(x - 1, -1, -1), range(y - 1, -1, -1)):
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for i, j in zip(range(x + 1, max), range(y - 1, -1, -1)):
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for i, j in zip(range(x - 1, -1, -1), range(y + 1, max)):
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for j in range(y + 1, max):
            i = x
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for j in range(y - 1, -1, -1):
            i = x
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for i in range(x + 1, max):
            j = y
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

        ok = False
        finish = False

        for i in range(x - 1, -1, -1):
            j = y
            if board._squares[i * 8 + j] == enemycolor:
                ok = True
            elif board._squares[i * 8 + j] == currentcolor:
                finish = True
                if ok is True:
                    MoveCalculator.change_colors(board, x, i, y, j, max, currentcolor)
                break
            elif board._squares[i * 8 + j] == SquareController.NONE:
                ok = False
                break

    @staticmethod
    def change_colors(board, xstart, xfinish, ystart, yfinish, max, color):
        xdiff = xfinish - xstart
        ydiff = yfinish - ystart
        signxdiff = int(math.copysign(1, xdiff))
        signydiff = int(math.copysign(1, ydiff))

        colorChanges = 0

        if xdiff != 0 and ydiff != 0:

            for i, j in zip(range(xstart, xfinish, signxdiff), range(ystart, yfinish, signydiff)):
                board._squares[i * 8 + j] = color
                colorChanges += 1

        elif xdiff == 0:
            for j in range(ystart, yfinish, signydiff):
                board._squares[xstart * 8 + j] = color
                colorChanges += 1
        elif ydiff == 0:
            for i in range(xstart, xfinish, signxdiff):
                board._squares[i * 8 + ystart] = color
                colorChanges += 1
        return colorChanges

    @staticmethod
    def get_possible_moves(board, color):
        empty_squares = []
        for i in range(0, 64):
            if board._squares[i] == SquareController.NONE:
                x = int(i / 8.0)
                y = i % 8
                empty_squares.append((x, y))
        possible = []
        for xy in empty_squares:
            if MoveCalculator.can_make_move(board, xy[0], xy[1], 8, color):
                possible.append(xy)
        return possible
