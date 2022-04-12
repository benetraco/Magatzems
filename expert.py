"""
Template file for expert.py module.
"""


import sys
import curses

from store import *


class Strategy:
    """Implementation of the expert strategy."""

    """
    Explicació:
    El programa es molt similar al simple.py l'única diferència és que en comptes de cada 
    vegada que arribi un nou container tornar a començar l'algorisme per la posició del principi
    seguirem per la posició on erem. Aquest programa millora el simple per un sol fet de probabilitat:
    si cada vegada comencem per les posicions del principi és menys probable que arribem a comprovar els
    containers de les útimes posicions i que, per tant, es caduquin abans de que els comprovem. Si 
    seguim des de la posició que haviem comprovat l'últim cop és més probable que quan comprovem els 
    containers de les últimes posicions encara es puguin vendre i en traiem valor.
    """

    _time: int
    _position: int
    _log: Logger
    _store: Store


    def __init__(self, width: int, log_path: str):
        self._log = Logger(log_path, "SimpleStrategy", width)
        self._store = Store(width)
        self._time = 0
        self._position = 0
    
    
    def cash(self) -> int:
        """Returns the store's cash at that moment"""

        return self._store.cash()

    
    def time(self) -> int:
        """Returns the time we are at that moment"""

        return self._time


    def update_time(self) -> None:
        """Updates the time once an action is done"""
    
        self._time += 1

    
    def position(self) -> int:
        """Returns the position we are at that moment"""

        return self._position


    def update_position(self) -> None:
        """Updates the position in which the program has to 
        operate based on the position it is operating"""

        if self._position == 0: self._position = 1
        elif self._position == 1: self._position = 2
        elif self._position == 2: self._position = 4
        elif self._position == 4: self._position = 6
        elif self._position == 6: self._position = 9
        elif self._position == 9: self._position = 12
        elif self._position == 12: self._position = 16
        else: self._position = 0 #self._position == 16


    def det_position_first_container(self, c_size: int) -> int:
        """Returns the position that has to go the container that arrives 
        to the store based on its size"""

        assert c_size <= 4
        if c_size == 1: return 0
        elif c_size == 2: return 2
        elif c_size == 3: return 6
        else: return 12 #c_size == 4


    def add_first_container(self, c: Container) -> None:
        """Adds the continer that arrives to the store the appropiate position
        The action is added to the logger."""

        p = self.det_position_first_container(c.size)
        self._store.add(c, p)
        self._log.add(self._time, c, p)
        self.update_time()


    def expired(self, c: Container) -> bool:
        """Returs if a container is expired at that moment"""

        return self.time() >= c.delivery.end


    def deliverable(self, c: Container) -> bool:
        """Returns if a container is deliverable at that moment"""

        return c.delivery.start <= self.time() and self.time() < c.delivery.end


    def remove_expired(self, c: Container) -> None:
        """
        Removes the continer c from the store without adding it's cash to the store.
        The actions are added to the logger.

        Pre: c is expired
        """

        self._store.remove(c)
        self._log.remove(self.time(), c)
        self._log.cash(self.time(), self.cash())
    

    def remove_deliverable(self, c: Container) -> None:
        """
        Removes de continer c from the store adding it's value to the store's cash.
        The actions are added to the logger.

        Pre: c is deliverable
        """

        self._store.add_cash(c.value)
        self._store.remove(c)
        self._log.remove(self.time(), c)
        self._log.cash(self.time(), self.cash())
    

    def move_next_or_before(self, c: Container, second: bool) -> None:
        """
        Moves the contanier c to the second stack or the the first stack
        of it's size depending on the bool "second".
        The action is added to the logger.

        Pre: c can be moved because is the top continer of the position of it's size
        """

        if second:
            self._store.move(c, self._position + c.size)
            self._log.move(self.time(), c, self._position + c.size)
        else:
            self._store.move(c, self._position - c.size)
            self._log.move(self.time(), c, self._position - c.size)


    def move_container_pila(self, c: Container, second: bool) -> None:
        """
        If the container is explired or can be delivered it is removed from the 
        container properly. If not it is moved to the second stack or the first 
        stack of it's size depending on the bool "second".
        
        Pre: c can be removed because is the top continer of the position of it's size
        """

        if self.expired(c):
            self.remove_expired(c)

        elif self.deliverable(c):
            self.remove_deliverable(c)

        else: #the top container of the position cannot be delivered neither is expired
            self.move_next_or_before(c, second)
        
        self.update_time()
            

    def exec(self, c: Container):
        """Apliquem l'excecució simple"""

        assert self._store.width() >= 20 
        #we make sure that the with of the store is 20 (if is smaller we cannot apply the simple strategy)

        self.add_first_container(c)

        #after we do an action we have to stop the algorithm if the next container arrives
        while self._time < c.arrival.end: 

            if self._store.empty(): #if the store is empty we don't have to do anything until the next container arrives
                self._time = c.arrival.end

            else: #until the position is empty we get all the containers from top to the bottom and follow the simple algorithm
                
                top_c = self._store.top_container(self._position)

                while top_c is not None and self._time < c.arrival.end: #we move all the containers from the first stack of the containers' size to the second
                    self.move_container_pila(top_c, True) #we write the bool True because we want to move the container second stack of it's size
                    top_c = self._store.top_container(self._position)

                self.update_position() 
                top_c = self._store.top_container(self._position)

                while top_c is not None and self._time < c.arrival.end: #we move all the containers from the second stack of the containers' size to the first
                    self.move_container_pila(top_c, False) #we write the bool False because we want to move the container first stack of it's size
                    top_c = self._store.top_container(self._position)

                self.update_position()


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

    execute_strategy(containers_path, log_path, width)
    check_and_show(containers_path, log_path, stdscr)


# start main script when program executed
if __name__ == '__main__':
    curses.wrapper(main)
