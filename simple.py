"""
Template file for simple.py module.
"""


import sys
import curses

from store import *


class Strategy: #ERROR! Hi ha algun bucle que no s'acaba
    """Implementation of the simple strategy."""

    _time: int
    _log: Logger
    _store: Store

    def __init__(self, width: int, log_path: str):
        self._log = Logger(log_path, "SimpleStrategy", width)
        self._store = Store(width)
        self._time = 0
    
    def cash(self) -> int:
        return self._store.cash()

    def determine_position(self, cont_size: int) -> int:
        """Returns the position of the first stack"""
        assert cont_size <= 4
        if cont_size == 1: return 0
        elif cont_size == 2: return 2
        elif cont_size == 3: return 6
        else: return 12 #cont_size == 4
    
    def determine_next_position(self, p: Position) -> int:
        if p == 0: return 1
        elif p == 1: return 2
        elif p == 2: return 4
        elif p == 4: return 6
        elif p == 6: return 9
        elif p == 9: return 12
        elif p == 12: return 16
        else: return 0 #p == 16

    def expired(self, c: Container, t: int) -> bool:
        """Returs if a container is expired at that moment"""
        return t >= c.delivery.end

    def can_deliver(self, c: Container, t: int) -> bool:
        """Returns if a container can be delivered at that moment"""
        return c.delivery.start <= t and t < c.delivery.end

    def move_continer_pila(self, c: Container, p: Position, t: int, next: bool) -> None:
        """
        Moves a continer to the next stack of it's size if bool "next" is True or to the stack 
        before if the bool "next" is False unless it can be removed from the store
        """
        if self.expired(c, t):
            self._store.remove(c)
            self._log.remove(t, c)
            self._log.cash(t, self._store.cash())
        elif self.can_deliver(c, t):
            self._store.add_cash(c.value)
            self._log.cash(t, self._store.cash())
            self._store.remove(c)
            self._log.remove(t, c)
        else: #the top container of the stack cannot be delivered neither is expired
            if next:
                self._store.move(c, p + c.size)
                self._log.move(t, c, p + c.size)
            else:
                self._store.move(c, p - c.size)
                self._log.move(t, c, p - c.size)
            
    def exec(self, c: Container): #ERROR! Hi ha algun bucle que no s'acaba
        """Apliquem la excecució simple"""
        assert self._store.width() >= 20
        self._time = c.arrival.start
        p = self.determine_position(c.size)
        self._store.add(c, p)
        self._log.add(self._time, c, p)
        self._time += 1
        stack = 0
        while self._time < c.arrival.end:
            while self._time < c.arrival.end and stack < self._store.width():
                if self._store.empty():
                    self._time += 1 #c.arrival.end
                else:
                    cont = self._store.top_container(stack)
                    while cont is not None and self._time < c.arrival.end:
                        self.move_continer_pila(cont, stack, self._time, True) #we write the bool True because we want to move the continer to the next stack
                        self._time += 1
                        cont = self._store.top_container(stack)
                    stack = self.determine_next_position(stack)
                    cont = self._store.top_container(stack)
                    while cont is not None and self._time < c.arrival.end:
                        self.move_continer_pila(cont, stack, self._time, False) #we write the bool False because we want to move the continer to the stack before
                        self._time += 1
                        cont = self._store.top_container(stack)
                    stack = self.determine_next_position(stack) #determines the next stack in which we have to operate based in the stack in which we are


def init_curses():
    """Initializes the curses library to get fancy colors and whatnots."""

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, curses.COLOR_WHITE, i)


def execute_strategy(containers_path: str, log_path: str, width: int):
    """Execute the strategy on an empty store of a certain width reading containers from containers_path and logging to log_path."""

    containers = read_containers(containers_path)
    strategy = Strategy(width, log_path)
    for container in containers:
        strategy.exec(container)


def main(stdscr: curses.window):
    """main script"""

    init_curses()

    containers_path = sys.argv[1]
    log_path = sys.argv[2]
    width = int(sys.argv[3])

    #print("h")
    execute_strategy(containers_path, log_path, width)
    #print("EXECUTED")
    check_and_show(containers_path, log_path, stdscr)


# start main script when program executed
if __name__ == '__main__':
    curses.wrapper(main)