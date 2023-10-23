class Game:
    def __init__(self):
        self.turn = 'X'
        self.board = ['','','','','','','','','',]
        self._win_states = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        self._inverse_player = {"X":"O","O":"X",}
    
    def Play(self, index: int) -> bool:
        if not self.board[index]:
            self.board[index] = self.turn
            self.turn = self._inverse_player[self.turn]
            return True
        else: return False

    def CheckWinner(self) -> str:
        __winner = -1
        for win_state in self._win_states:
            _a, _b, _c = [[self.board[i],i] for i in win_state]
            if (_a[0] or _b[0] or _c[0]) and (_a[0] == _b[0] == _c[0]): __winner = [self._inverse_player[self.turn],[_a[1],_b[1],_c[1]]]
        if len(''.join(self.board)) > 8 and __winner == -1: __winner = [2,None]
        return __winner

    def NewGame(self) -> None:
        Game.__init__(self)

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
                # TODO: Streamline these for loops
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
                e-=2*radius-1
                radius-=1

class TicTacToeRenderer:
    def __init__(self, renderer: RenderEngine,x_offset: int = 0, y_offset: int = 0, board_size: int = 500, line_thickness: int = 5, token_size: int = 10) -> None:
        self.renderer = renderer
        self.board_size = board_size
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.line_thickness = line_thickness
        self.token_size = token_size
        self.index_midpoints = [[round(board_size/6), round(board_size/6)], [round(board_size/2),round(board_size/6)], [round(board_size*5/6),round(board_size/6)],[round(board_size/6), round(board_size/2)], [round(board_size/2),round(board_size/2)], [round(board_size*5/6),round(board_size/2)],[round(board_size/6), round(board_size*5/6)], [round(board_size/2),round(board_size*5/6)], [round(board_size*5/6),round(board_size*5/6)], ]
        self.player_colours = {"X":self.renderer.COLOURS["WHITE"], "O":self.renderer.COLOURS["WHITE"]}
        self.functions_proxy = {"X": self.drawX, "O": self.drawO}

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

class KeyBoardEventManager:
    def __init__(self, keyboard_path: str = "/dev/input/event2"):
        self.KEYBOARD_DEVICE = keyboard_path
        self.KEYS = {27648:0,27136:1,26880:2,26368:3,7168:4,256:5,}
        self.UNKNOWN_EVENT = 1024
        self.EVENT_SIZE = 24
        self.DEVICE = open(self.KEYBOARD_DEVICE, "rb")

    def getInput(self):
        self.DEVICE.read(self.EVENT_SIZE) # Reads the unknow thing. TODO: figure out what that is for
        event_data = self.DEVICE.read(self.EVENT_SIZE)
        if len(event_data) != self.EVENT_SIZE:
            return 0
        data = bytearray(event_data)
        evtype = int.from_bytes(bytes(data[17:20]), byteorder='little')
        if evtype in self.KEYS and evtype!=self.UNKNOWN_EVENT:
            state = int.from_bytes(bytes(data[20:23]), byteorder='little')
            return [self.KEYS[evtype],state]
    
    def flushInputBuffer(self):
        if self.DEVICE:
            self.DEVICE.read(4096)

class BoardLogicHandler:
    def __init__(self, game: Game, boardRenderer: TicTacToeRenderer, renderEngine: RenderEngine):
        self.game = game
        self.boardRenderer = boardRenderer
        self.renderer = renderEngine
        self.cursorPosition = 0
        self.previousPosition = 0
        self.movements = [3,1,-1,-3]

    def start(self):
        self.renderEngine.initTerminal()
        self.boardRenderer.drawBoard()

    def moveCursor(self, event: int) -> bool:
        move = self.movements[event]
        if -1 < (self.cursorPosition + move) < 9:
            self.previousPosition = self.cursorPosition
            self.cursorPosition+=move
            self.resetPreviousTile()
            self.drawToken()
            self.renderer.updateFrameBuffer()
            return True
        else:
            return False
    
    def confirmPosition(self) -> bool:
        if self.game.Play(self.cursorPosition):
            self.boardRenderer.functions_proxy[self.game._inverse_player[self.game.turn]](self.cursorPosition, self.boardRenderer.player_colours[self.game._inverse_player[self.game.turn]])
            self.drawToken()
            self.renderer.updateFrameBuffer()
    
    def resetPreviousTile(self):
        _offset = round(self.boardRenderer.board_size/8)
        _mid = self.boardRenderer.index_midpoints[self.previousPosition]
        x1, y1, x2, y2 = [self.boardRenderer.x_offset + _mid[0] - _offset,self.boardRenderer.y_offset + _mid[1] - _offset,self.boardRenderer.x_offset + _mid[0] + _offset,self.boardRenderer.y_offset + _mid[1] + _offset]
        self.renderer.drawRectangle(x1,y1,x2,y2,self.renderer.COLOURS["BLACK"])
        if self.game.board[self.previousPosition]:
            self.boardRenderer.functions_proxy[self.game.board[self.previousPosition]](self.previousPosition, self.boardRenderer.player_colours[self.game._inverse_player[self.game.turn]])

    def drawToken(self) -> None:
        if self.game.board[self.cursorPosition]:
            self.boardRenderer.functions_proxy[self.game.turn](self.cursorPosition, self.renderer.COLOURS["RED"])
        else:
            self.boardRenderer.functions_proxy[self.game.turn](self.cursorPosition, self.renderer.COLOURS["PURPLE"])

    def updateBuffer(self) -> None:
        self.renderEngine.updateFrameBuffer()

def start():
    renderEngine = RenderEngine()
    boardRenderer = TicTacToeRenderer(renderEngine)
    mainGame = Game()
    board = BoardLogicHandler(mainGame,boardRenderer,renderEngine)
    renderEngine.initTerminal()
    keyboard = KeyBoardEventManager()
    boardRenderer.drawBoard()
    while True:
        userInput = keyboard.getInput()
        if userInput:
            if userInput[0] == 4 and userInput[1] == 1:
                board.confirmPosition()
                state = mainGame.CheckWinner()
                if state != -1:
                    print(state)
                    for token in state[1]:
                        boardRenderer.functions_proxy[state[0]](token,renderEngine.COLOURS["GREEN"])
                    renderEngine.updateFrameBuffer()
                    break
            elif userInput[0] == 5 and userInput[1] == 1:
                break
            elif userInput[1] == 1:
                board.moveCursor(userInput[0])
    keyboard.flushInputBuffer()
    exit(0)

if __name__ == "__main__":
    start()