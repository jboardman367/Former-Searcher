
from typing import List, Literal, Optional, Tuple


class Board:
    # cols[i][0] is the bottom element of the ith column
    cols: List[List[Literal['P', 'B', 'O', 'G']]]
    _groups: List[List[int]] = None
    _unbreakable_groups: List[List[int]] = None
    _n_groups: int = None
    _n_unbreakable_groups: int = None
    moves: int
    parent: Optional['Board']
    metadata: List[Tuple[str, str]]
    group_roots: List[Tuple[int, int]]
    def __init__(self, board: str=None, cols: List[Literal['P', 'B', 'O', 'G']]=None, moves=0, parent=None):
        self.moves = moves
        self.parent = parent
        self.metadata = []
        self.group_roots = []
        if board:
            rows = board.strip().split('\n')
            self.cols = [[r[i] for r in reversed(rows) if r[i] in ['P', 'O', 'B', 'G']] for i in range(len(rows[0]))]
        elif cols:
            self.cols = cols
        else:
            raise ValueError("Must provide either board string or columns")

    def move(self, col: int, row: int):
        if col < 0 or col >= len(self.cols):
            raise IndexError('Column index out of range')
        if row < 0 or row >= len(self.cols[col]):
            raise IndexError('Row index out of range')
        # We will create a copy of cols, do a recursive replacement with placeholder value,
        # then remove placeholder values and return a new board
        new_cols = [list(c) for c in self.cols]
        self._set_group_in_columns(new_cols, new_cols, col, row, '-')
        # remove placeholders
        new_cols = [[e for e in c if e != '-'] for c in new_cols]
        return Board(cols=new_cols, moves=self.moves+1, parent=self).with_metadata(last_move=f'({col}, {row})')
    
    def _set_group_in_columns(self, source, target, col, row, value):
        target_value = source[col][row]
        nodes = [(col, row)]
        visited = set()
        while len(nodes):
            _col, _row = nodes.pop()
            if (_col, _row) in visited:
                continue
            else:
                visited.add((_col, _row))
            target[_col][_row] = value
            # down
            if _row > 0 and source[_col][_row-1] == target_value:
                nodes.append((_col, _row-1)) 
            # up
            if _row + 1 < len(source[_col]) and source[_col][_row+1] == target_value:
                nodes.append((_col, _row+1))
            # left
            if _col > 0 and len(source[_col-1]) > _row and source[_col-1][_row] == target_value:
                nodes.append((_col-1, _row))
            # right
            if _col + 1 < len(source) and len(source[_col+1]) > _row and source[_col+1][_row] == target_value:
                nodes.append((_col+1, _row))

    def gmove(self, group: int):
        new_cols = [[r for j, r in enumerate(c) if self.groups[i][j] != group] for i, c in enumerate(self.cols)]
        return Board(cols=new_cols, moves=self.moves+1, parent=self).with_metadata(last_move=str(self.group_roots[group]))

    
    @property
    def groups(self):
        if self._groups == None:
            self._calculate_groups()
        return self._groups

    @property
    def unbreakable_groups(self):
        if self._unbreakable_groups == None:
            self._calculate_unbreakable_groups()
        return self._unbreakable_groups

    @property
    def n_groups(self):
        if self._n_groups == None:
            self._calculate_groups()
        return self._n_groups

    @property
    def n_unbreakable_groups(self):
        if self._n_unbreakable_groups == None:
            self._calculate_unbreakable_groups()
        return self._n_unbreakable_groups

    def _calculate_groups(self):
        self._groups = [[-1 for _ in c] for c in self.cols]
        group_id = -1
        for c in range(len(self.cols)):
            for r in range(len(self.cols[c])):
                if self._groups[c][r] == -1:
                    # Find the whole group at once
                    group_id += 1
                    self.group_roots.append((c, r))
                    self._set_group_in_columns(self.cols, self._groups, c, r, group_id)
        self._n_groups = group_id + 1
                    

    def _calculate_unbreakable_groups(self):
        self._unbreakable_groups = [[-1 for _ in c] for c in self.cols]
        group_id = -1
        for col_num, (col, g_col) in enumerate(zip(self.cols, self._unbreakable_groups)):
            last_color = None if col_num == 0 or len(self.cols[col_num-1]) == 0 else self.cols[col_num-1][0]
            for i in range(len(col)):
                if col[i] == last_color:
                    g_col[i] = group_id
                else:
                    group_id += 1
                    last_color = col[i]
                    g_col[i] = group_id
        self._n_unbreakable_groups = group_id + 1
    
    def _calculate_unbreakable_groups_v2(self):
        self._unbreakable_groups = [[-1 for _ in c] for c in self.cols]
        group_id = -1
        # We're going to try going in rows instead of columns
        # (group, column): (left: bool, right: bool)
        grounded = {}
        rows = max(len(c) for c in self.cols)

        for r in range(rows):
            for c, col in enumerate(self.cols):
                # skip if cell is empty (downside of going row first)
                if r >= len(col):
                    continue
                # cannot be separated from a cell below
                if r > 0 and col[r] == col[r-1]:
                    self._unbreakable_groups[c][r] = self._unbreakable_groups[c][r-1]
                # cannot be separated from cell on left if group is right-grounded
                elif c > 0 and col[r] == self.cols[c-1][r] and (r == 0 or grounded[(self._unbreakable_groups[c-1][r], c-1)][1]):
                    self._unbreakable_groups[c][r] = self._unbreakable_groups[c-1][r]
                    left_grounded = r == 0 or False
                    right_grounded = r == 0 or False

    
    @property
    def complete(self):
        return sum((len(c) for c in self.cols)) == 0
    
    def __str__(self):
        return '\n'.join(
            [f'### Moves: {self.moves} ###'] +
            [''.join([f'{i} '] + [c[i] if i < len(c) else ' ' for c in self.cols])
            for i in reversed(range(max((len(c) for c in self.cols))))]
            + [''.join(['  '] + [str(i) for i in range(len(self.cols))])]
            + [f'{k}: {v}' for k, v in self.metadata]
        )
    
    def with_metadata(self, **kwargs: str):
        for k, v in kwargs.items():
            self.metadata.append((k, v))
        return self


def main():
    cols = [
        ['O', 'B', 'O', 'G', 'O', 'O', 'P', 'P', 'P'],
        ['G', 'B', 'G', 'B', 'B', 'G', 'B', 'P', 'G'],
        ['B', 'B', 'O', 'G', 'P', 'P', 'B', 'P', 'G'],
        ['B', 'P', 'B', 'G', 'P', 'O', 'O', 'B', 'B'],
        ['G', 'B', 'B', 'O', 'O', 'B', 'O', 'P', 'P'],
        ['O', 'G', 'P', 'O', 'P', 'G', 'P', 'G', 'G'],
        ['B', 'P', 'B', 'O', 'P', 'O', 'O', 'P', 'B'],
    ]

    board = Board(cols=cols)
    n = 0
    print(f'\n### Moves: {n} ###')
    print(str(board))
    while not board.complete:
        try:
            move = input('> ')
            m1, m2 = move.split(',')
            board = board.move(int(m1), int(m2))
            n += 1
            print(f'\n### Moves: {n} ###')
            print(str(board))
        except Exception:
            print('Invalid move')

if __name__ == '__main__':
    main()