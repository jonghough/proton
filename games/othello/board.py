class Board(object):

    def __init__(self, board_controller):
        self._squares = []
        for sqr in board_controller._squares:
            for sq in sqr:
                self._squares.append(sq._currentcolor)

    def to_board_controller(self, board_controller):
        for x in range(0, 8):
            for y in range(0, 8):
                board_controller._squares[x][y].setColor(self._squares[x * 8 + y])

    @property
    def squares(self):
        return self._squares


    def print_me(self):

        def shape(n):
            if n == 1:
                return "o"
            elif n == -1:
                return "x"
            else: return " "
        st = ""
        for x in range(0, 8):
            st+="+-+-+-+-+-+-+-+-+\n"
            for y in range(0, 8):
                st+= "|"+shape(self._squares[y * 8 + x])+""
            st+="|\n"
        st+="+-+-+-+-+-+-+-+-+\n"
        print(st)
