
import re
from typing import Dict
from automata_tools import Automata
from automata_tools import utils
import NFAFromRegex
import xml.dom.minidom
import string

def process_regex(regex_string):
    
    #Case 1: regex string is empty
    if( len(regex_string) == 0 ):
        return

    #Case 2: regex string is just one whitespace
    if( len(regex_string) == 1 and regex_string == ' '):
        return

    #Regular expression to match against whitespaces in string
    pattern=r"\s+"

    formattedString = re.sub(pattern,"",regex_string)

    return formattedString

def convert_regex_to_nfa(regex_string):
    nfa: Automata = NFAFromRegex.NFAfromRegex(regex_string).getNFA()
    return nfa

def nfa_add_epsilon_states(state,nfa,eNfa: Automata):
    visited = set()
    statesSet = {state}
    while len(statesSet) != 0:
        currentState = statesSet.pop()
        if visited.__contains__(currentState) != True :
            visited.add(currentState)

def convert_states_set_to_dict(states):
    statesDictionary = {}
    
    index = 1

    for state in states:
        state = str(state)
        statesDictionary[state] = index
    
        index = index + 1
    
    return statesDictionary

def eNFA_to_DFA(nfa: Automata):
    minDFA: Automata = Automata()
    states = []
    transitions = []
    startState = []
    acceptStates = []
    initialEpsilonClosure = nfa.getEClosure(nfa.startstate) #1. Epsilon closure of start state

    #1. Add initial state to DFA
    startState.append(initialEpsilonClosure)
    states.append(initialEpsilonClosure)
    stack = []

    #Add to stack
    stack.append(initialEpsilonClosure)

    #Keep handling stack until empty
    while(len(stack) != 0):
        currentState: set = stack.pop()

        for symbol in nfa.language:
            newStateSet = set({})
            for state in currentState:
                currentSet = nfa.getReachableStates(state,symbol)
                if len(currentSet) != 0:
                    newStateSet.update(currentSet)
                    #Get union of epsilon closure of set
                    epsilon_closure_of_new_states = eNfa.getReachableStates(newStateSet,'\u03B5')

                    newStateSet = newStateSet.union(newStateSet,epsilon_closure_of_new_states)

                    if states.__contains__(newStateSet) != True:    #Check if state has been generated before and if not, add to dfa and stack
                        
                        states.append(newStateSet)
                        
                        stack.append(newStateSet)
                        
                        if(transitions.__contains__([currentState, newStateSet , symbol])) != True:
                            transitions.append([currentState, newStateSet , symbol])

    #Mark all final states.
    for statesSet in states:
        for finalState in nfa.finalstates:
            if statesSet.__contains__(finalState) == True:
                acceptStates.append(statesSet)
    
    #Create actual minDFA
    setDict = convert_states_set_to_dict(states)

    #Add transitions
    for t in transitions:
        minDFA.addtransition( setDict[str(t[0])] ,setDict[str(t[1])] ,t[2])
    
    #Set start state
    minDFA.setstartstate(setDict[ str(startState.pop())])

    #Set final states
    minDFA.finalstates = acceptStates.copy()

    return minDFA

def convert_state_letter_label(state):
    alphabet_latin = list(string.ascii_uppercase)
    return alphabet_latin[state - 1]

def outputXMLFile(minDFA: Automata):
    #NULL CHECK HERE

    xmlString = '<?xml version= "1.0" ?><automata><states>'
    
    for state in minDFA.states: #Add all states to xml
        xmlString = xmlString + '<'+convert_state_letter_label(state)+'></'+convert_state_letter_label(state)+'>'
    
    xmlString = xmlString + '</states>'
    
    xmlString = xmlString + '<transitions>'
    
    for key in minDFA.transitions.keys():
        startState = convert_state_letter_label(key)

        xmlString = xmlString + '<' + startState + '>'
        
        temp = minDFA.transitions.get(key)
        
        for tempKey in temp.keys():
            
            endState = convert_state_letter_label(tempKey)

            xmlString = xmlString + '<' + endState + '>' + temp.get(tempKey).pop() + '</' + endState + '>'
        
        xmlString = xmlString + '</' + startState + '>'

    xmlString  = xmlString + '</transitions></automata>'                    

    temp = xml.dom.minidom.parseString(xmlString)
    
    new_xml = temp.toprettyxml()

    with open("MinDFAXML.xml", "w") as f:
        f.write(new_xml)

def convert_eNfa_to_nfa(eNfa: Automata):
    newNfa = []
    automata = []
    finalStates = []
    eNfaStates = eNfa.states

    #1. Copy over all states in eNfa
    for state in eNfaStates:
        newNfa.append(state)
    
    #2. Set start state for nfa. 
    newNfaStartState = eNfa.startstate

    #3. Get all final states for e-NFA.
    finalStates.append(eNfa.finalstates)

    #4. Get all epsilon-reachable states

    #5. Get transitions
#    for i in range (1, len(eNfa.transitions) + 1):
#        transition = eNfa.transitions[i]
    for state in newNfa:
      transition = eNfa.transitions.get(state)  
      if(transition != None):
        for state in newNfa:
            transitionSymbol = transition.get(state)
            if(transitionSymbol != None):
                if transitionSymbol != None and ord(next(iter(transitionSymbol))) != ord('ε'):  #Check if ttransition is epsilopn transition.
                    #Add transition to newNFA if not
                    print("TODO")
try:
    #0. Get input string

    #1. Format input string
    processed_regex_string = process_regex("(ab)+c")

    print("Regex string",processed_regex_string)

    #2. Convert input string to e-NFA
    eNfa: Automata = convert_regex_to_nfa(processed_regex_string)

    #2.1. Print out intermediate e-NFA
    utils.drawGraph(eNfa, "E-NFA")

    #3. Convert NFA to DFA
    dfa: Automata = eNFA_to_DFA(eNfa)

    #4. Convert DFA to corresponding minDFA
    #nfa: Automata = convert_eNfa_to_nfa(eNfa)

    #5. Print minDFA to XML Document
    outputXMLFile(dfa)

    


except Exception:
    print("An exception has occured " + Exception)