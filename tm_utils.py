''' we store everything as strings
    states = letters 'A, 'B', 'C', ...
    directions = 'L' or 'R'
    symbols = '0', '1', ...
    machine code format is assumed to be:
    1RB0RB_1RC0LB_1LD1RE_1LB0LD_0RA---
    where halting may be denoted by ---, 1RZ, or 1RH if there are less than 8 states
    a machine with more than 2 tape symbols is encoded in the following format:
    1RB0RB2RC_1RC2LA0LB_1RB---2RA
'''
import copy

class TM:
    def __init__(self, code):
        if '---' in code:
            self.code = code
        elif '1RZ' in code:
            self.code = code.replace('1RZ', '---')
        else:
            self.code = code.replace('1RH', '---')

        code_fragments = self.code.split('_')
        self.tape_symbol_count = len(code_fragments[0]) // 3
        self.tm_state_count = len(code_fragments)
        self.__tm_states = ''.join(chr(ord('A') + i) for i in range(self.tm_state_count))
        self.__tape_symbols = ''.join(chr(ord('0') + i) for i in range(self.tape_symbol_count))
        self.tm_symbols = ''
        for i in range(self.tm_state_count):
            lower = chr(ord('a') + i)
            upper = chr(ord('A') + i)
            self.tm_symbols += (lower + upper)

    def __str__(self):
        return self.code

    def parse_combo_state(self, *args):
        ''' parses a combo state, which can be
            - lower/upper case a/A
            - tm_symbol followed by tape_symbol A0 A1 B0
            - a pair ('A', '0')
            and returns the last representation '''
        if len(args) == 2:
            tm_state, tape_symbol = args
        if len(args) == 1:
            combo_symbol = args[0]
            if len(combo_symbol) == 1:
                assert self.tape_symbol_count == 2
                tm_state = combo_symbol.upper()
                tape_symbol = '0' if combo_symbol.islower() else '1'
            else:
                tm_state, tape_symbol = combo_symbol[0], combo_symbol[1]
        assert tm_state in self.__tm_states
        assert tape_symbol in self.__tape_symbols
        return tm_state, tape_symbol

    def get_transition_info(self, *args):
        ''' arguments: tm_state and tape_symbol,
            return value: 
            new_tape_symbol,
            new_direction,
            new_tm_state '''
        tm_state, tape_symbol = self.parse_combo_state(*args)
        idx = self.__tm_states.index(tm_state) * (3 * self.tape_symbol_count + 1) + \
                self.__tape_symbols.index(tape_symbol) * 3
        return self.code[idx], self.code[idx + 1], self.code[idx + 2]

    def is_final(self, *args):
        tm_state, tape_symbol = self.parse_combo_state(*args)
        return self.get_transition_info(tm_state, tape_symbol) == ('-', '-', '-')

    def final_states(self):
        return [(tm_state, tape_symbol)
            for tm_state in self.tm_symbols 
            for tape_symbol in self.tape_symbols
            if self.is_final(tm_state, tape_symbol)]

    def simulation_step(self, left, symbol, right):
        ''' right part is always reversed '''
        new_tape_symb, new_direction, new_tm_state = self.get_transition_info(symbol)
        if new_direction == 'R':
            if right == '':
                right = '0'
            return left + new_tape_symb, (new_tm_state, right[-1]), right[:-1]
        if new_direction == 'L':
            if left == '':
                left = '0'
            return left[:-1], (new_tm_state, left[-1]), right + new_tape_symb

    def simulation_multiple_steps(self, _left, _symbol, _right, maxsteps):
        left = copy.deepcopy(_left)
        symbol = copy.deepcopy(_symbol)
        right = copy.deepcopy(_right)
        for i in range(maxsteps):
            if self.is_final(symbol):
                return left, symbol, right, i
            left, symbol, right = self.simulation_step(left, symbol, right)
        return left, symbol, right, maxsteps
