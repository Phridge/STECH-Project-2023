
import logging as l
l.basicConfig(filename="log.log", level=l.DEBUG)
l.debug("Programm gestartet")

from main_controller import main

#import statistic_lib.statistic_view
main()