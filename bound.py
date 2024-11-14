from typing import List, Tuple
from game import Board

def find_bounds(board: Board) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    max_upper_bound = board.n_unbreakable_groups
    # number of row-wise groups per colour, summed
    columns_with_g = ['G' in c for c in board.cols]
    columns_with_p = ['P' in c for c in board.cols]
    columns_with_o = ['O' in c for c in board.cols]
    columns_with_b = ['B' in c for c in board.cols]
    min_lower_bound = columns_with_g[0] + columns_with_p[0] + columns_with_o[0] + columns_with_b[0]
    for i in range(1, len(board.cols)):
        new_g = columns_with_g[i] and not columns_with_g[i-1]
        new_p = columns_with_p[i] and not columns_with_p[i-1]
        new_o = columns_with_o[i] and not columns_with_o[i-1]
        new_b = columns_with_b[i] and not columns_with_b[i-1]
        min_lower_bound += new_g + new_p + new_o + new_b
    # for now
    min_upper_bound = board.n_groups  # proof by I couldn't find a counterexample
    max_lower_bound = min_lower_bound
    return (min_lower_bound, min_upper_bound), (max_lower_bound, max_upper_bound)



# Is the number of groups an upper bound on minimum moves? Must try to """prove""" by lack of counterexample

def run_tests():
    case_names = []
    case_intervals = []
    case_strings = []
    with open('cases.txt', 'r') as f:
        interval_next_line = False
        for line in f.readlines():
            if interval_next_line:
                e1, e2 = line.strip().split(',')
                case_intervals.append((int(e1), int(e2)))
                case_strings.append('')
                interval_next_line = False
            elif line.startswith('#'):
                case_names.append(line.strip('# \n'))
                interval_next_line = True
            else:
                case_strings[-1] += line

    min_lower_error = 0
    min_upper_error = 0
    max_lower_error = 0
    max_upper_error = 0
    failed_cases = []
    for case_num in range(len(case_names)):
        print(f'Case {case_num}: {case_names[case_num]}')
        board = Board(board=case_strings[case_num])
        min_bounds, max_bounds = find_bounds(board)
        minimum, maximum = case_intervals[case_num]
        # If lower bound is higher than minimum or upper bound is lower than maximum
        if not (min_bounds[0] <= minimum <= min_bounds[1]):
            failed_cases.append(case_num)
            print(f'FAILED! got bounds {min_bounds} on minimum of {minimum}')
        if not (max_bounds[0] <= maximum <= max_bounds[1]):
            failed_cases.append(case_num)
            print(f'FAILED! got bounds {max_bounds} on maximum of {maximum}')
        else:
            min_le = minimum - min_bounds[0]
            min_ue = min_bounds[1] - minimum
            max_le = maximum - max_bounds[0]
            max_ue = max_bounds[1] - maximum
            print(f'minimum: {minimum}  bounds: {min_bounds}  error: ({min_le}, {min_ue})')
            print(f'maximum: {maximum}  bounds: {max_bounds}  error: ({max_le}, {max_ue})')
            min_lower_error += min_le
            min_upper_error += min_ue
            max_lower_error += max_le
            max_upper_error += max_ue

    print("## Summary ##")
    if len(failed_cases) > 0:
        print(f'Failed cases: {failed_cases}')
    print(f'lower error on minimum moves: {min_lower_error}')
    print(f'upper error on minimum moves: {min_upper_error}')
    print(f'lower error on maximum moves: {max_lower_error}')
    print(f'upper error on maximum moves: {max_upper_error}')
    print(f'total error on minimum moves: {min_lower_error + min_upper_error}')
    print(f'total error on maximum moves: {max_lower_error + max_upper_error}')
    print(f'total error: {min_lower_error + min_upper_error + max_lower_error + max_upper_error}')

if __name__ == '__main__':
    run_tests()