class Game:
    def __init__(self):
        self.turn = 'X'
        self.board = ['','','','','','','','','',]
        self._win_states = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        self._player_proxy =  {"X" : 0,"O" : 1,}
        self._inverse_player = {"X":"O","O":"X",}
        self._outcomes = ['X','O','T']
    
    def Play(self, index: int) -> bool:
        if not self.board[index]:
            self.board[index] = self.Turn
            self.turn = self._inverse_player[self.Turn]
            return True
        else: return False

    def CheckWinner(self) -> str:
        __winner = -1
        for win_state in self._win_states:
            _a, _b, _c = [self.board[i] for i in win_state]
            if (_a or _b or _c) and (_a == _b == _c): __winner = self._player_proxy[self._inverse_player[self.Turn]]
        if len(''.join(self.board)) > 8 and __winner == -1: __winner = 2
        return __winner

    def NewGame(self) -> None:
        Game.__init__(self)

class AI:
    def __init__(self, currentGame: Game, difficulty: int = 1, player: str = "O") -> None:
        self.currentGame = currentGame
        self.difficulty = difficulty
        self.player = player
        self.ALGORITHMS = [self.__easy__,self.__medium__]
        self.seeds = []
        self.players = ["X","O"]
        self._INVERSE_PROXY  = self.currentGame._inverse_player
        self.opponent = self._INVERSE_PROXY[self.player]
        self._WIN_STATES = currentGame._win_states
        self._hash_board = currentGame.board

    def play(self) -> list:
        return self.ALGORITHMS[self.difficulty]()

    def pseduoRandomGeneration(self, randRange: int) -> int:
        _seed = id(object()) + sum(self.seeds)
        _seed = (6364136223846793005 * _seed + 1) & 0xFFFFFFFFFFFFFFFF
        self.seeds.append(_seed)
        return _seed % randRange
    
    def __easy__(self) -> list:
        _grid = self.currentGame.Grid
        while True:
            _r = self.pseduoRandomGeneration(3)
            _c = self.pseduoRandomGeneration(3)
            if _grid[_r][_c] == '':
                return [_r,_c]

    def __medium__(self, easy_fallback=True):
        for win_state in self._WIN_STATES:
            _a = [self._hash_board[win_state[0]], win_state[0]]
            _b = [self._hash_board[win_state[1]], win_state[1]]
            _c = [self._hash_board[win_state[2]], win_state[2]]
            for player in [self.player, self.opponent]:
                if [_a[0], _b[0], _c[0]].count(player) == 2:
                    _remaining_tile = None
                    for i in [_a, _b, _c]:
                        if i[0] == '':
                            _remaining_tile = i[1]
                    if _remaining_tile is not None:
                        if self._hash_board[_remaining_tile] == '':
                            return _remaining_tile
                    
        return self.__easy__() if easy_fallback else 0

class RenderEngine:
    def __init__(self):
        with open('/sys/class/graphics/fb0/virtual_size') as size_file:
            self.WIDTH, self.HEIGHT = [int(i) for i in size_file.read().split(',')]
        size_file.close()
        del size_file
        with open('/sys/class/graphics/fb0/bits_per_pixel') as bits_file:
            self.BYTES_PER_PIXEL = int(bits_file.read()) // 8
        bits_file.close()
        del bits_file
        self.SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
        self.LOCAL_BUFFER = self.SYS_VIDEO_BUFFER.read()
        self.LOCAL_QUEUE = {}
        self.COLOURS = {"RED":b'\x00\x00\xFF\x00',"GREEN":b'\x00\xFF\x00\x00',"BLUE":b'\xFF\x00\x00\x00',"PURPLE":b'\xFF\x00\xFF\x00',"WHITE":b'\xFF\xFF\xFF\x00',"BLACK":b'\x00\x00\x00\x00',"YELLOW":b'\x00\xFF\xFF\x00',"PASTEL_PINK":b'\xFC\xCF\xF6\x00',}
    
    def queueLocalChange(self, x: int, y: int, Bytes: bytes) -> None:
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            position = (y * self.WIDTH + x) * self.BYTES_PER_PIXEL
            self.LOCAL_QUEUE[position] = Bytes

    def updateLocalBuffer(self) -> None:
        buffer_list = bytearray(self.LOCAL_BUFFER)
        for position in self.LOCAL_QUEUE:
            buffer_list[position:position+self.BYTES_PER_PIXEL] = self.LOCAL_QUEUE[position]
        self.LOCAL_BUFFER = bytes(buffer_list)
        self.LOCAL_QUEUE = {}

    def syncBuffers(self) -> None:
        self.SYS_VIDEO_BUFFER.seek(0)
        self.SYS_VIDEO_BUFFER.write(self.LOCAL_BUFFER)

    def updateFrameBuffer(self) -> None:
        self.updateLocalBuffer()
        self.syncBuffers()

    def clearFrameBuffer(self, Bytes: bytes = b'\x00\x00\x00\x00') -> None:
        for i in range(self.WIDTH):
            for j in range(self.HEIGHT):
                self.queueLocalChange(i,j,Bytes)
        self.updateFrameBuffer()

    def initTerminal(self) -> None:
        print("\x1b[2J\x1b[H",end="")
        self.clearFrameBuffer()
        print("\n"*(self.HEIGHT//14))

    def drawRectangle(self, start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes) -> None:
        for j in range(start_y, end_y):
            for i in range(start_x, end_x):
                self.queueLocalChange(i, j, colour)

    def drawLine(self, start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes, thickness: int = 3) -> None:
        slope = (end_y - start_y) / (end_x - start_x)
        c = start_y - slope * start_x
        for x in range(start_x, end_x + 1):
            for i in range(thickness+1):
                y = round(slope * (x+i) + c)
                self.queueLocalChange(x, y, colour)
                self.queueLocalChange(x, y - (i * 2), colour)

    def drawCircle(self, center_x: int, center_y: int, radius: int, colour: bytes, thickness: int = 3) -> None:
        e = -radius
        y = 0
        while y < radius:
            for i in range(thickness):
                for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    self.queueLocalChange(center_x + (radius*x_sign), center_y + (y*y_sign) + i, colour)
                for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    self.queueLocalChange(center_x + (y*y_sign), center_y + (radius*x_sign) + i, colour)
                for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    self.queueLocalChange(center_x + (radius*x_sign), center_y + (y*y_sign) - i, colour)
                for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    self.queueLocalChange(center_x + (y*y_sign), center_y + (radius*x_sign) - i, colour)
            e+=2*y+1
            y+=1
            if e >= 0:
                e -2*radius-1
                radius-=1

class TicTacToeBoard:
    def __init__(self, renderer: RenderEngine,x_offset: int = 0, y_offset: int = 0, board_size: int = 500, line_thickness: int = 5, token_size: int = 10) -> None:
        self.renderer = renderer
        self.board_size = board_size
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.line_thickness = line_thickness
        self.token_size = token_size
        self.index_midpoints = [[round(board_size/6), round(board_size/6)], [round(board_size/2),round(board_size/6)], [round(board_size*5/6),round(board_size/6)],[round(board_size/6), round(board_size/2)], [round(board_size/2),round(board_size/2)], [round(board_size*5/6),round(board_size/2)],[round(board_size/6), round(board_size*5/6)], [round(board_size/2),round(board_size*5/6)], [round(board_size*5/6),round(board_size*5/6)], ]

    def drawO(self, index: int, colour: bytes) -> None:
        x, y = self.index_midpoints[index]
        self.renderer.drawCircle(self.x_offset+x,self.y_offset+y,round(self.board_size*(self.token_size/100)),colour)

    def drawX(self, index: int, colour: bytes) -> None:
        s = round(self.board_size*(self.token_size/100))
        mid_x, mid_y = self.index_midpoints[index]
        self.renderer.drawLine(self.x_offset+mid_x-s,self.y_offset+mid_y-s,self.x_offset+mid_x+s,self.y_offset+mid_y+s,colour)
        self.renderer.drawLine(self.x_offset+mid_x-s,self.y_offset+mid_y+s,self.x_offset+mid_x+s,self.y_offset+mid_y-s,colour)

    def drawBoard(self):
        for i in [0.33,0.66]:
            offset = round(self.board_size * i)
            self.renderer.drawRectangle(self.x_offset,self.y_offset+offset,self.x_offset+self.board_size, self.y_offset+offset+self.line_thickness, self.renderer.COLOURS["WHITE"])
            self.renderer.drawRectangle(self.x_offset+offset,self.y_offset,self.x_offset+offset+self.line_thickness,self.y_offset+self.board_size, self.renderer.COLOURS["WHITE"])
        self.renderer.updateFrameBuffer()

def startGame() -> None:
    renderEngine = RenderEngine()
    board = TicTacToeBoard(renderEngine)
    game = Game()
    ai = AI(game)
    renderEngine.initTerminal()
    board.drawBoard()
    while True:
        gameStatus = game.CheckWinner()
        if gameStatus != -1:
            move = False
            while not move:
                user = int(input("Enter index"))
                move = game.Play(user)
        else:
            print(game._outcomes[gameStatus])


if __name__ == "__main__":
    startGame()