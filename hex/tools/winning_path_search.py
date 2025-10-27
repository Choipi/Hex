from .bitboard import Bitboard

__EMPTY = -1
__NOT_VISITED = 0
__VISITED = 1

PLAYER_O = 0
PLAYER_X = 1


def __add_to_path_return_true(tile: int, dim: int,
                              path: list[tuple[str, int]]) -> bool:
    position = (chr(tile % dim + ord('a')), tile // dim + 1)
    path.append(position)
    return True


def __add_if_in_bitboard(winning_bitboard: Bitboard,
                         position: int, neighbors_list: list[int]) -> None:
    if winning_bitboard.get_bit(position) == 1:
        neighbors_list.append(position)


def __add_north_neighbors(winning_bitboard: Bitboard, dim: int, row: int,
                          column: int, neighbors_list: list[int]) -> None:
    # Not checking northern neighbors if first row
    if row > 0:
        if column < dim - 1:
            position = (row - 1) * dim + column + 1  # NORTH EAST
            __add_if_in_bitboard(winning_bitboard, position, neighbors_list)
        position = (row - 1) * dim + column  # NORTH WEST
        __add_if_in_bitboard(winning_bitboard, position, neighbors_list)


def __add_south_neighbors(winning_bitboard: Bitboard, dim: int, row: int,
                          column: int, neighbors_list: list[int]) -> None:
    # Not checking southern neighbors if last row
    if row < dim - 1:
        position = (row + 1) * dim + column  # SOUTH EAST
        __add_if_in_bitboard(winning_bitboard, position, neighbors_list)
        if column > 0:
            position = (row + 1) * dim + column - 1  # SOUTH WEST
            __add_if_in_bitboard(winning_bitboard, position, neighbors_list)


def __add_east_neighbor(winning_bitboard: Bitboard, dim: int, row: int,
                        column: int, neighbors_list: list[int]) -> None:
    # Not checking eastern neighbors if last column
    if column < dim - 1:
        position = row * dim + column + 1  # EAST
        __add_if_in_bitboard(winning_bitboard, position, neighbors_list)


def __add_west_neighbor(winning_bitboard: Bitboard, dim: int, row: int,
                        column: int, neighbors_list: list[int]) -> None:
    # Not checking western neighbors if first column
    if column > 0:
        position = row * dim + column - 1  # WEST
        __add_if_in_bitboard(winning_bitboard, position, neighbors_list)


def __neighbors(player: int, tile: int,
                winning_bitboard: Bitboard, dim) -> list[int]:
    neighbors_list: list[int] = []
    row = tile // dim
    column = tile % dim
    # If white won we want to first visit the southern neighbors
    if player == PLAYER_O:
        __add_south_neighbors(winning_bitboard, dim, row,
                              column, neighbors_list)
        __add_east_neighbor(winning_bitboard, dim, row,
                            column, neighbors_list)
        __add_west_neighbor(winning_bitboard, dim, row,
                            column, neighbors_list)
        __add_north_neighbors(winning_bitboard, dim, row,
                              column, neighbors_list)
    # If black won we want to first visit the eastern neighbors
    else:
        __add_east_neighbor(winning_bitboard, dim, row,
                            column, neighbors_list)
        __add_south_neighbors(winning_bitboard, dim, row,
                              column, neighbors_list)
        __add_north_neighbors(winning_bitboard, dim, row,
                              column, neighbors_list)
        __add_west_neighbor(winning_bitboard, dim, row,
                            column, neighbors_list)
    return neighbors_list


def __visit(tile: int, player: int, winning_bitboard: Bitboard, dim: int,
            visited: list[int], path: list) -> bool:
    visited[tile] = __VISITED
    # If white won the end of the search is the bottom row
    if player == PLAYER_O and tile // dim == dim - 1:
        return __add_to_path_return_true(tile, dim, path)
    # If black won the end of the search is the rightmost column
    if player == PLAYER_X and tile % dim == dim - 1:
        return __add_to_path_return_true(tile, dim, path)

    for neighbor in __neighbors(player, tile, winning_bitboard, dim):
        if visited[neighbor] == __NOT_VISITED:
            if __visit(neighbor, player, winning_bitboard,
                       dim, visited, path):
                # Recursively add the tile to the path if the end of the
                # search has been reached.
                return __add_to_path_return_true(tile, dim, path)
    return False


def __dfs(player: int, winning_bitboard: Bitboard, dim: int,
          visited: list[int]) -> list[tuple[str, int]]:
    path: list[tuple[str, int]] = []
    for i in range(dim):
        tile_to_visit = -1
        # If white won we want to start each search on the top row
        if player == PLAYER_O and visited[i] == __NOT_VISITED:
            tile_to_visit = i
        # If black won we want to start each search on the leftmost column
        elif player == PLAYER_X and visited[i * dim] == __NOT_VISITED:
            tile_to_visit = i * dim
        # If no tile to visit is found check the
        # next column (white) or line (black)
        if tile_to_visit == -1:
            continue
        # If a path is found return the path in a from top to bottom (white)
        # or from left to right order (black)
        if __visit(
                tile_to_visit,
                player,
                winning_bitboard,
                dim,
                visited,
                path):
            path.reverse()
            return path
    raise ValueError("No connecting path has been found")


def winning_path_search(player: int, winning_bitboard: Bitboard,
                        dim: int) -> list[tuple[str, int]]:
    """
    Uses a depth first search to find the winning connecting path of
    the winning player.

    Parameters
    ----------
    player: int
        winning player
    winning_bitboard: Bitboard
        winning player's bitboard
    dim: int
        dimension of the board

    Returns
    -------
    list[tuple[str, int]]
        winning connecting path of the player
    """
    visited = []
    for i in range(dim * dim):
        if winning_bitboard.get_bit(i) == 1:
            visited.append(__NOT_VISITED)
        else:
            visited.append(__EMPTY)
    return __dfs(player, winning_bitboard, dim, visited)
