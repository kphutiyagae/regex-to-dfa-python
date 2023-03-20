from automata_tools import Automata
from automata_tools import utils
import NFAFromRegex

nfa: Automata = NFAFromRegex.NFAfromRegex('ab*c').getNFA()

utils.drawGraph(nfa, 'test')
