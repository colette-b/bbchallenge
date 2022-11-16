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
        self.__tape_symbol_count = len(code_fragments[0]) / 3
        self.__state_count = len(code_fragments)
        self.shortcode = self.code.replace('_', '')
        self.tm_symbols = ''
        for i in range(self.state_count()):
            lower = chr(ord('a') + i)
            upper = chr(ord('A') + i)
            self.tm_symbols += (lower + upper)

    def state_count(self):
        return self.__state_count
    
    def tape_symbol_count(self):
        return self.__tape_symbol_count

    def __str__(self):
        return self.code

    def get_transition_info(self, symbol, tm_symb=None):
        ''' arguments: one of symbols aAbBcCdDeE
            return value: 
            symbol left behind '0' or '1',
            direction 'R' or 'L', 
            next state one of 'ABCDE' '''
        try:
            idx = self.tm_symbols.index(symbol) * 3
        except:
            print(f'got symbol {symbol}')
            raise Exception()
        return self.shortcode[idx], self.shortcode[idx + 1], self.shortcode[idx + 2]

    def is_final(self, tm_symb):
        x, _, _ = self.get_transition_info(tm_symb)
        return x == '-'

    def final_states(self):
        return [tm_symb for tm_symb in self.tm_symbols if self.is_final(tm_symb)]

    def simulation_step(self, left, symbol, right):
        ''' right part is always reversed '''
        b, direction, s = self.get_transition_info(symbol)
        if direction == 'R':
            if right == '':
                right = '0'
            return left + b, (s.upper() if right[-1]=='1' else s.lower()), right[:-1]
        if direction == 'L':
            if left == '':
                left = '0'
            return left[:-1], (s.upper() if left[-1]=='1' else s.lower()), right + b

    def simulation_multiple_steps(self, _left, _symbol, _right, maxsteps):
        left = copy.deepcopy(_left)
        symbol = copy.deepcopy(_symbol)
        right = copy.deepcopy(_right)
        for i in range(maxsteps):
            if self.is_final(symbol):
                return left, symbol, right, i
            left, symbol, right = self.simulation_step(left, symbol, right)
        return left, symbol, right, maxsteps

TM_SKELET_LIST = [68329601,
55767995,
5950405,
6897876,
60581745,
58211439,
7196989,
7728246,
12554268,
3810716,
3810169,
4982511,
7566785,
31357173,
2204428,
20569060,
1365166,
15439451,
14536286,
347505,
9980689,
45615747,
6237150,
60658955,
47260245,
13134219,
7163434,
5657318,
6626162,
4986661,
56967673,
6957734,
11896833,
11896832,
11896831,
13609549,
7512832,
35771936,
9914965,
3841616,
5915217,
57874080,
5878998]