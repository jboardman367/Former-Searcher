from heapq import heappush, heappop
from typing import List, Tuple

from bound import find_bounds
from game import Board
from freemoves import do_free_moves_max, do_free_moves_min
import time as time

def search_min(board: Board, visit_limit, discard_duplicate_scores=True, report_distance=100000):
    # keep a buffer of boards sorted by (min_upper+n, -n, min_lower+n, entry_count)
    boards: List[Tuple[int, int, int, int, Board]] = []
    heappush(boards, (0, 0, 0, 0, do_free_moves_min(board).with_metadata(i='0')))
    visits = 0

    start_time = time.time()
    cur_time = start_time

    # Prune is the lowest seen value of (min_upper+n). Values with (min_lower+n) > prune are pruned.
    prune = 9999999
    solutions: List[Board] = []
    while visits < visit_limit and len(boards) > 0:
        parent: Board
        mln: int
        _, _, mln, _, parent = heappop(boards)
        if mln > prune:
            continue

        children = [parent.gmove(group) for group in range(parent.n_groups)]
        children = [do_free_moves_min(child) for child in children if find_bounds(child)[0][0] + child.moves < prune]

        for child in children:
            visits += 1
            if visits % report_distance == 0:
                print(f"{visits} boards searched, t = {round(time.time() - start_time)}. Time for last {report_distance/1000}k: {round((time.time() - cur_time) * 100) / 100}. Estimated time to completion is {round((time.time() - start_time)/visits * (visit_limit - visits))}s. Best is {prune + (1 if discard_duplicate_scores else 0)}")
                cur_time = time.time()
            if child.complete:
                if len(solutions) == 0 or child.moves < solutions[0].moves:
                    # Set prune one lower to discard branches equal to current best solution
                    prune = child.moves - (1 if discard_duplicate_scores else 0)
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
    print(f'Total time {time.time() - start_time}')
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

def search_max(board: Board, visit_limit, discard_duplicate_scores=True, report_distance=100000):
    # keep a buffer of boards sorted by (-max_lower-n, -n, -max_upper-n, entry_count)
    boards: List[Tuple[int, int, int, int, Board]] = []
    heappush(boards, (0, 0, 0, 0, do_free_moves_max(board).with_metadata(i='0')))
    visits = 0
    fake_visits = 0

    start_time = time.time()
    cur_time = start_time

    # Prune is the lowest seen value of (-max_lower-n). Values with (-max_upper-n) > prune are pruned.
    prune = 9999999
    highest_depth = 0
    solutions: List[Board] = []
    while fake_visits < visit_limit and len(boards) > 0:
        parent: Board
        mun: int
        _, _, mun, _, parent = heappop(boards)
        if mun > prune:
            continue

        children = sorted([parent.gmove(group) for group in range(parent.n_groups)], key=lambda child: find_bounds(child)[1][1], reverse=True)
        fake_visits += len(children)
        children = [do_free_moves_max(child) for child in children if -find_bounds(child)[1][1] - child.moves < prune]

        for child in children:
            visits += 1
            if visits % report_distance == 0:
                print(f"{fake_visits} boards searched, t = {round(time.time() - start_time)}. Time for last {report_distance/1000}k: {round((time.time() - cur_time) * 100) / 100}. Estimated time to completion is {round((time.time() - cur_time) * (visit_limit - visits) / report_distance)}s. Best is {prune + (1 if discard_duplicate_scores else 0)}")
                cur_time = time.time()
            
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
                break
            if -max_lower - n < prune:
                prune = -max_lower - n
            heappush(boards, (-max_lower - n, - n, -max_upper -n, visits, child.with_metadata(upper=str(max_upper+n), lower=str(max_lower+n), i=str(visits))))
    print(f'Total time {time.time() - start_time}')
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
    with open('board.txt', 'r') as f:
        board_string = f.read(10_000)
    bd = Board(board=board_string)
    search_min(bd, visit_limit=1e7, discard_duplicate_scores=True, report_distance=100000)
