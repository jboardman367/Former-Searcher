
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
        if c in total_visited:
            continue
        # skip empty columns
        if len(col) == 0:
            continue
        # if there's nothing above the group, it will be at the top of every column it spans
        top = len(col) - 1
        group_id = board.groups[c][top]
        color = col[top]
        
        group = []
        for gc,group_col in enumerate(board.groups):
            for r,id in enumerate(group_col):
                if id == group_id:
                    group.append((gc, r))
                
        # keep track of column span
        colmin = min(group[i][0] for i in range(len(group)))
        colmax = max(group[i][0] for i in range(len(group)))
        
        topbottom_mismatch = any(board.cols[i][-1] != color for i in range(colmin, colmax + 1))

        # keep track of groups visited previously
        total_visited.update(range(colmin, colmax + 1))
        
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
        
        # find this full group
        group_id = board.groups[c][first]
        group = []
        for gc,group_col in enumerate(board.groups):
            for r,id in enumerate(group_col):
                if id == group_id:
                    group.append((gc, r))

        # keep track of column span
        colmin = min(group[i][0] for i in range(len(group)))
        colmax = max(group[i][0] for i in range(len(group)))
        
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
            group_id = board.groups[cell[0]][cell[1]]
            group = []
            for gc,group_col in enumerate(board.groups):
                for r,id in enumerate(group_col):
                    if id == group_id:
                        group.append((gc, r))
            
            mingroup = min(group[i][0] for i in range(len(group)))
            maxgroup = max(group[i][0] for i in range(len(group)))

            if mingroup < colmin and maxgroup > colmax:
                outspanned = True
                break

        if outspanned:
            continue


        # we've eliminated all columns that either move something or could merge, so make the move
        return do_free_moves_min(board.move(c, first).with_metadata(free_move='true')) 
            
    # is removing a colour always optimal? It definitely is with 2 colours remaining, not sure otherwise.
    return board
