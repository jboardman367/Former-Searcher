from heapq import heappush, heappop
from typing import List, Tuple

from bound import find_bounds
from game import Board
from freemoves import do_free_moves_max, do_free_moves_min

def search_min(board: Board, visit_limit, discard_duplicate_scores=True):
    # keep a buffer of boards sorted by (min_upper+n, -n, min_lower+n, entry_count)
    boards: List[Tuple[int, int, int, int, Board]] = []
    heappush(boards, (0, 0, 0, 0, do_free_moves_min(board).with_metadata(i='0')))
    visits = 0
    # Prune is the lowest seen value of (min_upper+n). Values with (min_lower+n) > prune are pruned.
    prune = 9999999
    solutions: List[Board] = []
    while visits < visit_limit and len(boards) > 0:
        parent: Board
        mln: int
        _, _, mln, _, parent = heappop(boards)
        if mln > prune:
            continue
        for group in range(parent.n_groups):
            visits += 1
            child = do_free_moves_min(parent.gmove(group))
            if child.complete:
                if len(solutions) == 0 or child.moves < solutions[0].moves:
                    # Set prune one lower to discard branches equal to current best solution
                    prune = child.moves - discard_duplicate_scores
                    solutions = [child]
                elif child.moves == solutions[0].moves:
                    solutions.append(child)
                else:
                    continue
            (min_lower, min_upper), _ = find_bounds(child)
            n = child.moves
            if min_lower + n > prune:
                continue
            if min_upper + n < prune:
                prune = min_upper + n
            heappush(boards, (min_upper+n, -n, min_lower+n, visits, child.with_metadata(lower=str(min_lower+n), upper=str(min_upper+n), i=str(visits))))
    if len(solutions) == 0:
        print(f'No solutions found within visit limit ({visits} boards visited)')
        return
    print(f'Best solution: {solutions[0].moves} ({len(solutions)} occurrences)')
    print(f'Boards visited: {visits}')
    input('Press enter to see a solution')
    parent = solutions[0]
    board_strings = []
    while parent != None:
        board_strings.append(str(parent))
        parent = parent.parent
    for s in reversed(board_strings):
        print(s)

def search_max(board: Board, visit_limit, discard_duplicate_scores=True):
    # keep a buffer of boards sorted by (-max_lower-n, -n, -max_upper-n, entry_count)
    boards: List[Tuple[int, int, int, int, Board]] = []
    heappush(boards, (0, 0, 0, 0, do_free_moves_max(board).with_metadata(i='0')))
    visits = 0
    # Prune is the lowest seen value of (-max_lower-n). Values with (-max_upper-n) > prune are pruned.
    prune = 9999999
    highest_depth = 0
    solutions: List[Board] = []
    while visits < visit_limit and len(boards) > 0:
        parent: Board
        mun: int
        _, _, mun, _, parent = heappop(boards)
        if mun > prune:
            continue
        for group in range(parent.n_groups):
            visits += 1
            child = do_free_moves_max(parent.gmove(group))
            if child.complete:
                if len(solutions) == 0 or child.moves > solutions[0].moves:
                    solutions = [child]
                    # Set prune one lower to discard branches equal to current best solution
                    prune = -child.moves - discard_duplicate_scores
                elif child.moves == solutions[0].moves:
                    solutions.append(child)
                else:
                    continue
            _, (max_lower, max_upper) = find_bounds(child)
            n = child.moves
            highest_depth = max(n, highest_depth)
            if -max_upper - n > prune:
                continue
            if -max_lower - n < prune:
                prune = -max_lower - n
            heappush(boards, (-max_lower - n, - n, -max_upper -n, visits, child.with_metadata(upper=str(max_upper+n), lower=str(max_lower+n), i=str(visits))))
    if len(solutions) == 0:
        print(f'No solutions found within visit limit ({visits} boards visited, max depth {highest_depth})')
        return
    print(f'Best solution: {solutions[0].moves} ({len(solutions)} occurrences)')
    print(f'Boards visited: {visits}')
    for i in range(len(solutions)):
        input(f'Press enter to see solution {i}')
        parent = solutions[i]
        board_strings = []
        while parent != None:
            board_strings.append(str(parent))
            parent = parent.parent
        for s in reversed(board_strings):
            print(s)

if __name__ == '__main__':
    with open('241115.txt', 'r') as f:
        board_string = f.read(10_000)
    bd = Board(board=board_string)
    search_max(bd, visit_limit=1e6, discard_duplicate_scores=True)
