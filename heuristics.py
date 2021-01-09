#
# additional extra evaluations
#

def hamming(candidate_board, solved_board, size_rows, size_cols):  # aka tiles out of place
    res = 0
    for i in range(size_rows * size_cols):
        if candidate_board[i] != 0 and candidate_board[i] != solved_board[i]:
            res += 1
    return res


# lim deve diminuire -> 0
def hamming_delta(candidate_board_r1, candidate_board_r2, solved_board, size_rows, size_cols):
    r1 = hamming(candidate_board_r1, solved_board, size_rows, size_cols)
    r2 = hamming(candidate_board_r2, solved_board, size_rows, size_cols)
    return (r1 - r2) / (size_rows * size_cols)  # normalized to [0..1]