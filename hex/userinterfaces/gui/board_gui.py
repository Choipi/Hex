import math
import os
import gi
from gi.repository import Gtk, Gdk, Graphene, Gsk
gi.require_version('Gtk', '4.0')
from hex.tools.logger import LogLevel, log
from hex.tools.game_over_state import GameOverState
from hex.tools.game_state import GameState


class BoardWidget(Gtk.Widget):
    """
    A Gtk Widget in charge of displaying the game's board and handling
    player interactions with the board.

    Attributes
    ----------
    game: Game_State
        pointer to the game manager
    game_dim: int
        the dimension of the board. Example: for a 9x9 board, dim = 9
    rect_dim: float
        size of the square that will contain an hexagon
    character_offset: float
        reserved space where a character will be drawn
    y_offset: float
        y space between two hexagons inside the same column
    x_offset: float
        x space between two hexagons inside the same column
    virt_width: float
        default width that will be used for click handling and scaling
    virt_height: float
        default height that will be used for click handling and
        scaling
    current_scale: float
        the scale of the real height and width compared to the
        defaults
    board_rects: list[list[Graphene.Rect]]
        list containing the bounding boxes of each hexagon

    Methods
    -------
    - inside_which_hexagon(self, real_x: float, real_y: float)
            -> Union[Graphene.Rect, int, int]:
        Checks if the given coordinates are inside an hexagon and \
        if found return the hexagon's data.
    - is_inside_hexagon(self, rect: Graphene.Rect,
                          x: float, y: float) -> bool:
        Check if the point (x, y) is inside the hexagon of the \
        given bounding box.
    - on_clicked(self, gesture: Gtk.GestureClick, n_press: int,
                   real_x: float, real_y: float) -> None:
        Mouse click handler. If the click is inside an hexagon, play \
        the corresponding move and refresh the board's display.
    - do_snapshot(self, snapshot: Gtk.Snapshot) -> None:
        Main display function. It is called each window resize or \
        when self.queue_draw() is called.
    - update_dimensions(self, snapshot: Gtk.Snapshot) -> None:
        Each time the window gets resized, scale the coordinate \
        system of the drawing.
    - initialize_board_rects(self) -> None:
        Initialize every hexagon bounding boxes according to the \
        size of the board.
    - draw_borders_and_text(self, snapshot: Gtk.Snapshot) -> None:
        Draw the borders and the characters around the board using \
        snapshot and cairo.
    - draw_white_borders(self, snapshot: Gtk.Snapshot) -> None:
        Draw the white borders above and below the board using two \
        rounded rectangles with an outline.
    - draw_black_borders(self, cairo):
        Draw the black borders on the right side and on the left \
        side of the board by filling a rhombus drawn with cairo.
    - draw_characters(self, cairo):
        Draw the letters corresponding to the columns above the \
        board and the numbers corresponding to the rows on the left \
        side using cairo.
    - draw_board(self, snapshot: Gtk.Snapshot) -> None:
        Draw the board and render images of hexagons corresponding \
        to their state in the board in their bounding boxes.
    - draw_winning_path(self, snapshot: Gtk.Snapshot) -> None:
        Draw the winning path by rendering the winning version of \
        the hexagon image on each bounding box composing the winning \
        path.
    """
    __EMPTY_HEX = Gdk.Texture.new_from_filename(
        os.path.dirname(__file__) + "/resources/hex.png")
    __WHITE_HEX = Gdk.Texture.new_from_filename(
        os.path.dirname(__file__) + "/resources/hex_white.png")
    __BLACK_HEX = Gdk.Texture.new_from_filename(
        os.path.dirname(__file__) + "/resources/hex_black.png")
    __BLACK_WINNING_HEX = Gdk.Texture.new_from_filename(
        os.path.dirname(__file__) + "/resources/hex_black_winning.png")
    __WHITE_WINNING_HEX = Gdk.Texture.new_from_filename(
        os.path.dirname(__file__) + "/resources/hex_white_winning.png")
    __DEFAULT_WIDGET_DIM = 1000
    __DEFAULT_FONT_SIZE = 55
    __BORDER_OUTLINE_WIDTH = 3

    def __init__(self, game: GameState, use_cairo=True):
        """ BoardWidget's constructor.

        Parameters
        ----------
        game: Game_State
            access to the game's data and logic
        use_cairo: bool
            when set to False the characters and black borders will
            not be displayed
        """
        super().__init__()
        # Configure the window to be expandable
        self.set_size_request(-1, -1)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Pointer to the game logic
        self.__game = game

        # Will be used to compute different spaces
        self.__game_dim = game.get_game_dim()

        # SPACES
        self.__rect_dim = self.__DEFAULT_WIDGET_DIM / self.__game_dim
        self.__character_offset = 0.
        if use_cairo:
            self.__character_offset = self.__rect_dim
        # y_offset == height of the hexagon minus a diagonal
        self.__y_offset = self.__rect_dim * .75
        self.__x_offset = self.__rect_dim / 2
        self.__virt_width = self.__DEFAULT_WIDGET_DIM \
            + (self.__game_dim - 1) * self.__x_offset \
            + self.__character_offset
        self.__virt_height = self.__DEFAULT_WIDGET_DIM \
            - (self.__game_dim - 1) * (self.__rect_dim - self.__y_offset) \
            + self.__character_offset

        # scale between the real and default dimensions of the window
        self.__current_scale = 1.

        # Initalizing bounding boxes
        self.__board_rects: list[list[Graphene.Rect]] = []
        self.__initialize_board_rects()

    def __inside_which_hexagon(self,
                             real_x: float,
                             real_y: float) -> tuple[None,
                                                     int,
                                                     int] | tuple[Graphene.Rect,
                                                                  int,
                                                                  int]:
        """ Checks if the given coordinates are inside an hexagon and
        if found return the hexagon's data.

        Parameters
        ----------
        real_x: float
            unscaled x coordinate of the handled click on the window
        real_y: float
            unscaled y coordinate of the handled click on the window

        Returns
        -------
        Graphene.Rect, int, int
            the bounding box and board coordinates of an hexagon
            if there is one at the given coordinates
        None, -1, -1
            if there is no hexagon
        """
        # Set coordinates of the window to coordinates of the snapshot
        virt_x = real_x / self.__current_scale
        virt_y = real_y / self.__current_scale
        # Compute the origin of the clicked rectangle
        y = (virt_y - self.__character_offset) // self.__y_offset
        x = (virt_x - self.__character_offset -
             y * self.__x_offset) // self.__rect_dim
        y = math.floor(y)
        x = math.floor(x)
        log(LogLevel.DEBUG, "GUI Click handling: Rectangle " +
            chr(x + ord('a')) + str(y + 1) + " contains the click")
        # Check if the computed rectangle is  within the board
        if x < -1 or y < 0 or x >= self.__game_dim or y > self.__game_dim:
            return None, -1, -1
        # Rounding method excludes the bottom left quadrant at limits
        if y == self.__game_dim:
            y = self.__game_dim - 1
            if x >= 0 and x < self.__game_dim - 1:
                x += 1
        if x == -1:
            x = 0
        hexagons = []
        hexagons.append((self.__board_rects[y][x], x, y))
        if y > 0:
            # north neighbor (top left)
            hexagons.append((self.__board_rects[y - 1][x], x, y - 1))
            if x < self.__game_dim - 1:
                # north east neighbor (top right)
                hexagons.append(
                    (self.__board_rects[y - 1][x + 1], x + 1, y - 1))
        if y < self.__game_dim - 1:
            # south neighbor (bottom right)
            hexagons.append((self.__board_rects[y + 1][x], x, y + 1))
            if x > 0:
                # south west neighbor (bottom left)
                hexagons.append(
                    (self.__board_rects[y + 1][x - 1], x - 1, y + 1))
        for hex in hexagons:
            if self.__is_inside_hexagon(hex[0], virt_x, virt_y):
                return hex[0], hex[1], hex[2]
        return None, -1, -1

    def __is_inside_hexagon(self, rect: Graphene.Rect,
                          x: float, y: float) -> bool:
        """ Check if the point (x, y) is inside the hexagon of the
        given bounding box.

        Parameters
        ----------
        rect: Graphene.Rect
            an hexagon bounding box
        x: float
            scaled x coordinate
        y: float
            scaled y coordinate

        Returns
        -------
        True
            if the point is inside the hexagon
        False
            if the point is outside the hexagon
        """
        # Check whether the point is both below the diagonal and
        # before the side
        rect_center = rect.get_center()
        dx = abs(x - rect_center.x)
        dy = abs(y - rect_center.y)
        r = self.__rect_dim / 2
        return dy < (r - dx) / 2 + r / 2 and dx < r

    def on_clicked(self, gesture: Gtk.GestureClick, n_press: int,
                   real_x: float, real_y: float) -> bool:
        """
        Mouse click handler. If the click is inside an hexagon, play
        the corresponding move and refresh the board's display.

        Parameters
        ----------
        gesture: Gtk.GestureClick
            reference to the gesture object
        n_press: int
            number of times a click has been detected at these
            coordinates
        real_x: int
            unscaled x coordinate
        real_y: int
            unscaled y coordinate
        """
        if not self.__game.is_game_over():
            clicked_hex, board_x, board_y = self.__inside_which_hexagon(
                real_x, real_y)
            if clicked_hex is not None:
                board_pos = (chr(ord('a') + board_x), board_y + 1)
                log(LogLevel.DEBUG,
                    f"GUI User interaction: Played move {board_pos[0]}{board_pos[1]}")
                if self.__game.play_move(board_pos) == 0:
                    return True
        return False

    def do_snapshot(self, snapshot: Gtk.Snapshot) -> None:
        """
        Main display function. It is called each window resize or when
        self.queue_draw() is called.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        self.__update_dimensions(snapshot)
        self.__draw_board(snapshot)
        log(LogLevel.DEBUG, "GUI: Board refreshed")

    def __update_dimensions(self, snapshot: Gtk.Snapshot) -> None:
        """
        Each time the window gets resized, scale the coordinate system
        of the drawing.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        width = self.get_width()
        height = self.get_height()
        shortest_by_ratio = min(
            width, height * self.__virt_width / self.__virt_height)
        if shortest_by_ratio == width:
            self.__current_scale = width / self.__virt_width
        else:
            self.__current_scale = height / self.__virt_height
        snapshot.scale(self.__current_scale, self.__current_scale)

    def __initialize_board_rects(self) -> None:
        """
        Initialize every hexagon bounding boxes according to the size
        of the board.
        """
        for i in range(self.__game_dim):
            self.__board_rects.append([])
            row_y_offset = self. __character_offset + i * self.__y_offset
            row_x_offset = self.__character_offset + i * self.__x_offset
            for j in range(self.__game_dim):
                x = row_x_offset + j * self.__rect_dim
                y = row_y_offset
                rect = Graphene.Rect().init(x, y,
                                            self.__rect_dim, self.__rect_dim)
                self.__board_rects[i].append(rect)

    def __draw_borders_and_text(self, snapshot: Gtk.Snapshot) -> None:
        """
        Draw the borders and the characters around the board using
        snapshot and cairo.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        cairo_bounds = Graphene.Rect().init(0, 0, self.__virt_width,
                                            self.__virt_height)
        c = snapshot.append_cairo(cairo_bounds)
        if self.__game_dim > 1:
            self.__draw_white_borders(snapshot)
            self.__draw_black_borders(c)
        self.__draw_characters(c)

    def __draw_white_borders(self, snapshot: Gtk.Snapshot) -> None:
        """
        Draw the white borders above and below the board using two
        rounded rectangles with an outline.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        white = Gdk.RGBA()
        white.parse("#ffffff")
        black = Gdk.RGBA()
        black.parse("#000000")

        # Top White border
        x = self. __character_offset + self.__rect_dim / 2
        y = self. __character_offset
        width = self.__rect_dim * (self.__game_dim - 1)
        height = self.__rect_dim
        top_white_border = Graphene.Rect().init(x, y, width, height)
        outline = Gsk.RoundedRect()
        outline.init_from_rect(top_white_border, radius=5)
        snapshot.append_color(white, top_white_border)
        snapshot.append_border(outline, [self.__BORDER_OUTLINE_WIDTH, 0, 0, 0],
                               [black, black, black, black])
        # Bottom White border
        x = self. __character_offset + self.__x_offset * \
            (self.__game_dim - 1) + self.__rect_dim / 2
        y = self. __character_offset + self.__y_offset * (self.__game_dim - 1)
        bottom_white_border = Graphene.Rect().init(x, y, width, height)
        outline.init_from_rect(bottom_white_border, radius=5)
        snapshot.append_color(white, bottom_white_border)
        snapshot.append_border(outline, [0, 0, self.__BORDER_OUTLINE_WIDTH, 0],
                               [black, black, black, black])

    def __draw_black_borders(self, cairo):
        """
        Draw the black borders on the right side and on the left side
        of the board by filling a rhombus drawn with cairo.

        Parameters
        ----------
        cairo
            a cairo context
        """
        cairo.set_source_rgb(0, 0, 0)
        cairo.set_line_width(3)

        top_left_hex_x = self. __character_offset
        bottom_left_hex_x = self. __character_offset \
            + self.__x_offset * (self.__game_dim - 1)
        top_right_border_x = top_left_hex_x + self.__rect_dim * self.__game_dim
        bottom_hex_y = self. __character_offset \
            + self.__y_offset * (self.__game_dim - 1)
        # Draw lines from top left to bottom left to bottom right to
        # top right and back to top left and then fill the rhombus.
        cairo.move_to(top_left_hex_x,
                      top_left_hex_x + self.__rect_dim * 3 / 4)
        cairo.line_to(bottom_left_hex_x,
                      bottom_hex_y + self.__rect_dim * 3 / 4)
        cairo.line_to(bottom_left_hex_x + self.__rect_dim,
                      bottom_hex_y)
        cairo.line_to(bottom_left_hex_x + self.__rect_dim * self.__game_dim,
                      bottom_hex_y + self.__rect_dim / 4)
        cairo.line_to(top_right_border_x,
                      self. __character_offset + self.__rect_dim / 4)
        cairo.fill()

    def __draw_characters(self, cairo):
        """
        Draw the letters corresponding to the columns above the board
        and the numbers corresponding to the rows on the left side
        using cairo.

        Parameters
        ----------
        cairo
            a cairo context
        """
        cairo.select_font_face("Sans")
        cairo.set_font_size(self.__DEFAULT_FONT_SIZE *
                            self.__current_scale * 10 / self.__game_dim)
        # Draw letters
        for i in range(self.__game_dim):
            cairo.move_to(self.__character_offset / 1.2 + i * self.__rect_dim,
                          self.__character_offset / 1.1)
            cairo.show_text(chr(i + ord('A')))
        # Draw numbers
        for i in range(self.__game_dim):
            if (i >= 9):
                x = i * self.__x_offset - self.__character_offset / 6 \
                    - self.__game_dim / 2
            else:
                x = i * self.__x_offset + self.__character_offset / 6 \
                    - self.__game_dim / 2
            y = self.__character_offset + i * self.__y_offset \
                + self.__rect_dim / 1.4
            cairo.move_to(x, y)
            cairo.show_text(str(i + 1))

    def __draw_board(self, snapshot: Gtk.Snapshot) -> None:
        """
        Draw the board and render images of hexagons corresponding to
        their state in the board in their bounding boxes.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        self.__draw_borders_and_text(snapshot)
        for i in range(self.__game_dim):
            for j in range(self.__game_dim):
                board_position = i * self.__game_dim + j
                tile = self.__game.get_value_of_space(board_position)
                rect = self.__board_rects[i][j]
                match tile:
                    case 0:
                        snapshot.append_texture(self.__EMPTY_HEX, rect)
                    case 1:
                        snapshot.append_texture(self.__WHITE_HEX, rect)
                    case 2:
                        snapshot.append_texture(self.__BLACK_HEX, rect)
                    case _:
                        raise ValueError(
                            "An unknown value has been read when"
                            + "trying to draw the board's tiles.")
        if self.__game.is_game_over():
            self.__draw_winning_path(snapshot)

    def __draw_winning_path(self, snapshot: Gtk.Snapshot) -> None:
        """
        Draw the winning path by rendering the winning version of the
        hexagon image on each bounding box composing the winning path.

        Parameters
        ----------
        snapshot: Gtk.Snapshot
            a drawing area using hardware accelerated rendering
        """
        winning_path = self.__game.get_winning_path()
        for hex in winning_path:
            x = ord(hex[0]) - ord('a')
            y = hex[1] - 1
            rect = self.__board_rects[y][x]
            match self.__game.get_winner():
                case GameOverState.WHITE_WON:
                    snapshot.append_texture(self.__WHITE_WINNING_HEX, rect)
                case GameOverState.BLACK_WON:
                    snapshot.append_texture(self.__BLACK_WINNING_HEX, rect)
                case _:
                    raise ValueError(
                        "Drawing a winning path despite having no winner")
