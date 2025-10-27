from threading import Timer, get_ident
from time import perf_counter
from signal import signal, pthread_kill, SIGUSR1
from .game_over_state import GameOverState
from .logger import LogLevel, log


DEFAULT_INTERVAL = 0.01
MINUTE = 60.


class TimerThread(Timer):
    """ A thread that will periodically update the remaining times.

    Attributes
    ----------
    interval: int
        the interval of time at which the thread will call its
        function
    function: int
        size of the board's bitboards. It's always equal to dim * dim
    """

    def __init__(self, interval, function):
        super().__init__(interval, function, None, None)

    def run(self) -> None:
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def handler(sig, frame):
    """
    Intercepts SIGUSR1 and raises InterruptedError to interrupt
    system calls like input().
    """
    raise InterruptedError("One of blitz mode's timer finished")


class BlitzTimer:
    """ A class handling timers for the game's blitz mode.

    Attributes
    ----------
    game_state: Game_State
        reference to the game to set its game over state
    current_player: int
        the player whose timer is active
    default_time: int
        base time that will be used to reset both timers
    w_remaining_time: float
        white's remaining time
    b_remaining_time: float
        black's remaining time
    timer: TimerThread
        thread that will periodically update the remaining times
    time_measure: float
        intermediary time measure used between timer intervals
    total_time: float
        total game time elapsed

    Methods
    -------

    update_remaining_times -> None:
        Function called by the timer thread to update the remaining
        times and to update and notify the game when a timer runs out.
    start -> None:
        Start the timer thread and set the first intermediary
        time measure.
    resume -> None:
        Resume the timer by reinitializing the thread and take
        a new intermediary time measure.
    pause -> None:
        Pause the timer by cancelling the thread.
    reset -> None:
        Pause the timer, reset the remaining time and reinitialize
        the timer thread.
    set_default_time(minutes: int) -> None:
        Change the base time of the timers.
    next_player -> None:
        Switch to the other player's timer and set a new
        intermediary time measure.
    get_white_remaining_time -> float:
        Get white's remaining time.
    get_black_remaining_time(self) -> float:
        Get black's remaining time.
    """

    def __init__(self, game_state, minutes: int):
        """ Initialize the Blitz timer.

        Parameters
        ----------

        game_state: Game_State
            reference to the game
        minutes: int
            base time of the timers in minutes
        """
        # Game informations
        self.__game_state = game_state
        self.__current_player = game_state.get_current_player()

        # Base time that will be used to reset both timers
        self.__default_time = minutes * MINUTE

        # timers
        self.__w_remaining_time = minutes * MINUTE
        self.__b_remaining_time = minutes * MINUTE

        # Initialize the thread
        self.__timer = TimerThread(DEFAULT_INTERVAL,
                                   self.update_remaining_times)
        self.__timer.daemon = True

        # Time measures
        self.__time_measure = 0.
        self.__total_time = 0.

        # Setup signal handling
        self.__caller = get_ident()
        signal(SIGUSR1, handler)

        # Display refreshing functions for the gui
        def f(): return None
        self.__refresh_function = [f, f]

    def __timer_ran_out(self, winner: GameOverState) -> None:
        """ Notify the game that a timer ran out. """
        self.__game_state.set_game_over(winner)
        pthread_kill(self.__caller, SIGUSR1)
        elapsed = perf_counter() - self.__total_time
        log(LogLevel.INFO, "Total time elapsed: {0:.0f}:{1:.2f}"
            .format(elapsed // 60, elapsed % 60))
        self.__refresh_function[1]()
        self.pause()

    def update_remaining_times(self) -> None:
        """
        Function called by the timer thread to update the remaining
        times and to update and notify the game when a timer runs out.
        """
        # Update remaining time
        if self.__current_player == 0:
            self.__w_remaining_time -= perf_counter() - self.__time_measure
        else:
            self.__b_remaining_time -= perf_counter() - self.__time_measure

        # Update the intermediary time measure for the next call
        self.__time_measure = perf_counter()

        # Refresh the timer in the gui
        self.__refresh_function[0]()

        # Notify the game if a timer runs out.
        if self.__w_remaining_time <= 0:
            self.__w_remaining_time = 0  # for display purposes
            self.__timer_ran_out(GameOverState.BLACK_WON)
        elif self.__b_remaining_time <= 0:
            self.__b_remaining_time = 0  # for display purposes
            self.__timer_ran_out(GameOverState.WHITE_WON)

    def start(self) -> None:
        """
        Start the timer thread and set the first intermediary
        time measure.
        """
        current_time = perf_counter()
        self.__time_measure = current_time
        self.__total_time = current_time
        self.__timer.start()
        log(LogLevel.INFO, "Blitz mode timer started")

    def resume(self) -> None:
        """
        Resume the timer by reinitializing the thread and take
        a new intermediary time measure.
        """
        self.__timer = TimerThread(DEFAULT_INTERVAL,
                                   self.update_remaining_times)
        self.__timer.daemon = True
        current_time = perf_counter()
        self.__total_time = current_time \
            - self.__time_measure \
            + self.__total_time
        self.__time_measure = current_time
        self.__timer.start()
        log(LogLevel.INFO, "Blitz mode timer resumed")

    def pause(self) -> None:
        """ Pause the timer by cancelling the thread. """
        self.__timer.cancel()
        log(LogLevel.INFO, "Blitz mode timer paused")

    def reset(self) -> None:
        """
        Pause the timer, reset the remaining time and reinitialize
        the timer thread.
        """
        self.pause()
        self.__timer.join()
        self.__w_remaining_time = self.__default_time
        self.__b_remaining_time = self.__default_time
        self.__timer = TimerThread(DEFAULT_INTERVAL,
                                   self.update_remaining_times)
        self.__timer.daemon = True

    def set_default_time(self, minutes: int) -> None:
        """ Change the base time of the timers.

        Parameters
        ----------
        minutes: int
            time in minutes
        """
        self.__default_time = minutes * MINUTE

    def next_player(self) -> None:
        """
        Switch to the other player's timer and set a new
        intermediary time measure.
        """
        self.__current_player = (self.__current_player + 1) % 2
        self.__time_measure = perf_counter()

    def get_white_remaining_time(self) -> float:
        """ Get white's remaining time. """
        return_value = self.__w_remaining_time
        return return_value

    def get_black_remaining_time(self) -> float:
        """ Get black's remaining time. """
        return_value = self.__b_remaining_time
        return return_value

    def get_default_time(self) -> float:
        """ Get default time. """
        return self.__default_time

    def set_white_remaining_time(self, time_amount: float) -> None:
        """ Set white's remaining time.

        Parameters
        ----------
        time_amount: float
            amount of time
        """
        self.__w_remaining_time = time_amount

    def set_black_remaining_time(self, time_amount: float) -> None:
        """ Set black's remaining time.

        Parameters
        ----------
        time_amount: float
            amount of time
        """
        self.__b_remaining_time = time_amount

    def set_gui_refresh_methods(self, function):
        self.__refresh_function = function
