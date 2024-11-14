
from game import Board


def do_free_moves_max(board: Board):
    # look for groups that won't move anything and are just in one column
    for c, col in enumerate(board.cols):
        for r in reversed(range(len(col))):
            # If we get to the end of the group without breaking, we can get rid of the
            # top of the column
            if r + 1 < len(col) and col[r+1] != col[r]:
                return do_free_moves_max(board.move(c, r+1).with_metadata(free_move='true'))
            # If we're connected to something on the left, break
            if (c > 0 and len(board.cols[c-1]) > r and board.cols[c-1][r] == col[r]):
                break
            # If we're connected to something on the right, break
            if (c + 1 < len(board.cols) and len(board.cols[c+1]) > r and board.cols[c+1][r] == col[r]):
                break
            # If we're at the bottom and not connected left or right, we can get rid of the group
            if r == 0:
                return do_free_moves_max(board.move(c, 0).with_metadata(free_move='true'))

    return board

def do_free_moves_min(board: Board):
    cols_with_color = {
        'G': ['G' in c for c in board.cols],
        'P': ['P' in c for c in board.cols],
        'O': ['O' in c for c in board.cols],
        'B': ['B' in c for c in board.cols],
    }
    # for c, col in enumerate(board.cols):
    #     if len(col) == 0:
    #         continue
    #     top_color = col[-1]
    #     # If the color exists in a neighboring column, continue
    #     if c > 0 and cols_with_color[top_color][c-1] or c + 1 < len(board.cols) and cols_with_color[top_color][c+1]:
    #         continue
    #     could_connect_below = False
    #     for r, color in enumerate(col):
    #         # If we see the same color as the top but don't see it directly above, it could connect below
    #         if r + 1 < len(col) and color == top_color and col[r+1] != top_color:
    #             could_connect_below = True
    #             break
    #     # If there's no way we could connect with something below us, free move
    #     if not could_connect_below:
    #         return do_free_moves_min(board.move(c, len(col)-1).with_metadata(free_move='true'))
        
    # isolated groups with nothing above them
    total_visited = set()
    for c, col in enumerate(board.cols):
        # skip empty columns
        if len(col) == 0:
            continue
        # if there's nothing above the group, it will be at the top of every column it spans
        top = len(col) - 1
        color = col[top]
        # ignore if we've already visited as part of a previous group
        if (c, top) in total_visited:
            continue
        # keep track of column span
        colmin = c
        colmax = c
        # walk the group
        nodes = [(c, top)]
        group = set()
        topbottom_mismatch = False
        while len(nodes) > 0:
            _col, _row = nodes.pop()
            group.add((_col, _row))
            colmin = min(colmin, _col)
            colmax = max(colmax, _col)
            # above
            if _row + 1 < len(board.cols[_col]):
                if board.cols[_col][_row+1] == color:
                    if (_col, _row+1) not in group:
                        nodes.append((_col, _row+1))
                else:
                    topbottom_mismatch = True
                    break
            # below
            if _row > 0 and board.cols[_col][_row-1] == color:
                if (_col, _row-1) not in group:
                    nodes.append((_col, _row-1))
            # left
            if _col > 0 and len(board.cols[_col-1]) > _row and board.cols[_col-1][_row] == color:
                if (_col-1, _row) not in group:
                    nodes.append((_col-1, _row))
            # right
            if _col + 1 < len(board.cols) and len(board.cols[_col+1]) > _row and board.cols[_col+1][_row] == color:
                if (_col+1, _row) not in group:
                    nodes.append((_col+1, _row))

        # keep track of groups visited previously
        total_visited.update(group)
        
        if topbottom_mismatch:
            continue

        # check if group could merge
        # left or right
        if colmin > 0 and cols_with_color[color][colmin-1] or colmax + 1 < len(board.cols) and cols_with_color[color][colmax+1]:
            continue
        # below - is there a tile within the column span of matching color that isn't in the group
        could_merge_down = False
        for _c in range(colmin, colmax+1):
            for _r in range(len(board.cols[_c])):
                if board.cols[_c][_r] == color and (_c, _r) not in group:
                    could_merge_down = True
                    break
            if could_merge_down:
                break
        
        if could_merge_down:
            continue

        # we've eliminated all columns that either move something or could merge, so make the move
        return do_free_moves_min(board.move(c, top).with_metadata(free_move='true'))
        

    # isolated groups where the only colour above is the colour directly below for each column
    for c, col in enumerate(board.cols):
        # skip empty columns
        if len(col) == 0:
            continue
        # This will always occur in groups with at least one column where it is the second group down
        first = -1
        for i in reversed(range(len(col)-1)):
            if col[i] != col[-1]:
                first = i
                break
        if first == -1:
            continue  # column doesn't have two groups
        color = col[first]
        # ignore if we've already visited as part of a previous group
        if (c, first) in total_visited:
            continue
        # keep track of column span
        colmin = c
        colmax = c
        # walk the group
        nodes = [(c, first)]
        group = set()
        while len(nodes) > 0:
            _col, _row = nodes.pop()
            group.add((_col, _row))
            colmin = min(colmin, _col)
            colmax = max(colmax, _col)
            # above
            if _row + 1 < len(board.cols[_col]) and board.cols[_col][_row+1] == color:
                    if (_col, _row+1) not in group:
                        nodes.append((_col, _row+1))
            # below
            if _row > 0:
                if board.cols[_col][_row-1] == color:
                    if (_col, _row-1) not in group:
                        nodes.append((_col, _row-1))
            # left
            if _col > 0 and len(board.cols[_col-1]) > _row and board.cols[_col-1][_row] == color:
                if (_col-1, _row) not in group:
                    nodes.append((_col-1, _row))
            # right
            if _col + 1 < len(board.cols) and len(board.cols[_col+1]) > _row and board.cols[_col+1][_row] == color:
                if (_col+1, _row) not in group:
                    nodes.append((_col+1, _row))
        
        # check if group could merge
        # left or right
        if colmin > 0 and cols_with_color[color][colmin-1] or colmax + 1 < len(board.cols) and cols_with_color[color][colmax+1]:
            continue
        # below - is there a tile within the column span of matching color that isn't in the group
        # OR any sequence of matching colour that has a non-matching colour above has a different non-matching colour below
        # OR any element on top has a column span greater than the removed group
        could_merge_down = False
        mismatched = False
        check_span_of = []
        closed = True
        for _c in range(colmin, colmax+1):
            if len(board.cols[c]) == 0:
                continue
            top_color = None
            # closed tracks whether the last seen tile is top_color. True by
            # default so if the group takes up the whole column, it passes.
            # Locked tracks whether there's been a color other than top_color and the group color
            closed = True
            locked = False
            # whenever we reopen, we'll need to put the above in check_span_of
            for _r in reversed(range(len(board.cols[_c]))):
                if board.cols[_c][_r] == color:
                    if (_c, _r) not in group:
                        could_merge_down = True
                        break
                    if locked:
                        mismatched = True
                        break
                    if top_color and closed:
                        closed = False
                        check_span_of.append((_c, _r+1))
                elif board.cols[_c][_r] == top_color:
                    closed = True
                else:
                    if top_color is None:
                        top_color = board.cols[_c][_r]
                        closed = True
                    elif not closed:
                        mismatched = True
                        break
                    elif closed:
                        locked = True

            if could_merge_down or mismatched or not closed:
                break
        
        if could_merge_down or mismatched or not closed:
            continue

        checked_span_of = set()
        outspanned = False
        for cell in check_span_of:
            # don't double up
            if cell in checked_span_of:
                continue
            nodes = [cell]
            mingroup = cell[0]
            maxgroup = cell[0]
            group_id = board.groups[cell[0]][cell[1]]
            while len(nodes) > 0:
                _c, _r = nodes.pop()
                checked_span_of.add((_c, _r))
                mingroup = min(mingroup, _c)
                maxgroup = max(maxgroup, _c)
                # above
                if _r + 1 < len(board.groups[_c]) and board.groups[_c][_r+1] == group_id:
                    if (_c, _r+1) not in checked_span_of:
                        nodes.append((_c, _r+1))
                # below
                if _r > 0 and board.groups[_c][_r-1] == group_id:
                    if (_c, _r-1) not in checked_span_of:
                        nodes.append((_c, _r-1))
                # left
                if _c > 0 and len(board.groups[_c-1]) > _r and board.groups[_c-1][_r] == group_id:
                    if (_c-1, _r) not in checked_span_of:
                        nodes.append((_c-1, _r))
                # right
                if _c + 1 < len(board.groups) and len(board.groups[_c+1]) > _r and board.groups[_c+1][_r] == group_id:
                    if (_c+1, _r) not in checked_span_of:
                        nodes.append((_c+1, _r))
            if mingroup < colmin and maxgroup > colmax:
                outspanned = True

        if outspanned:
            continue


        # we've eliminated all columns that either move something or could merge, so make the move
        return do_free_moves_min(board.move(c, first).with_metadata(free_move='true'))
        
            
    # is removing a colour always optimal? It definitely is with 2 colours remaining, not sure otherwise.
    return board