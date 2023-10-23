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
        _grid = self.currentGame.board
        while True:
            _r = self.pseduoRandomGeneration(3)
            _c = self.pseduoRandomGeneration(4)
            result = _r + _c
            if _grid[result] == '':
                return [result]

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