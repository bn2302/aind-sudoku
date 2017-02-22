assignments = []


def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

# Names of the rows and columns in the grid

rows = 'ABCDEFGHI'
cols = '123456789'

# Create the labels for the elements of the sudoku grid
boxes = cross(rows, cols)

# define the row column and diag units
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]

# add units for diagonal sudoku
diagonal_units_diag = [[rows[i] + cols[i] for i, _ in enumerate(rows)]]
diagonal_units_revdiag = [[rows[i] + cols[len(cols)-1-i]
                          for i, _ in enumerate(rows)]]

# Unitlist and peers to store the neighbors of the current element in a
# dictionary
unitlist = row_units + column_units + square_units + diagonal_units_diag +\
    diagonal_units_revdiag
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Input:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Output:
        the values dictionary with the naked twins eliminated from peers.
    """

    for unit in unitlist:

        # Identify the naked twins
        # Get elements with same string
        twins = {i: values[i] for i in unit if len(values[i]) == 2}

        # Change keys and values of the naked twin dict
        flipped_twins = {}
        for key, value in twins.items():
            if value not in flipped_twins:
                flipped_twins[value] = [key]
            else:
                flipped_twins[value].append(key)

        nkd_twins = {key: value for key, value in flipped_twins.items()
                     if len(value) > 1}

        # Remove the naked twins from the values
        for key, value in nkd_twins.items():
            for unit_member in unit:
                if unit_member not in value:
                    values = assign_value(values, unit_member,
                                          values[unit_member].replace(
                                              key[0], ""))
                    values = assign_value(values, unit_member,
                                          values[unit_member].replace(
                                              key[1], ""))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.

    Input: grid(string) - A grid in string form.

    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
                then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.

    Input: values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    print


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value,
    eliminate this value from the values of all its peers.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer,
                                  values[peer].replace(digit, ""))
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that
    only fits in one box, assign the value to this box.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box
    with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same,
    return the sudoku.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys()
                                    if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys()
                                   if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree and solve
    the sudoku.
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities

    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.

    Input: grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Output: The dictionary representation of the final sudoku grid.
                False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
