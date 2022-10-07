# we store everything as strings
# states = letters
# directions = 'L' or 'R'
# symbols = '0' or '1'

class TM:
    states = 'ABCDE'
    tm_symbols = 'aAbBcCdDeE'

    def __init__(self, code):
        self.new_symbol = dict()
        self.move_dir = dict()
        self.new_state = dict()
        self.code = code
        code_fragments = code.split('_')
        self.shortcode = code.replace('_', '')
        for state, code_fragment in zip(TM.states, code_fragments):
            self.new_symbol[state, '0'] = code_fragment[0]
            self.move_dir[state, '0'] = code_fragment[1]
            self.new_state[state, '0'] = code_fragment[2]
            self.new_symbol[state, '1'] = code_fragment[3]
            self.move_dir[state, '1'] = code_fragment[4]
            self.new_state[state, '1'] = code_fragment[5]

    def state_count(self):
        return len(self.new_symbol)

    def __str__(self):
        compact_code = ''
        for state in TM.states:
            for symbol in [0, 1]:
                compact_code = compact_code + \
                    self.new_symbol[state, symbol] + \
                    self.move_dir[state, symbol] + \
                    self.new_state[state, symbol] + \
                    ('_' if symbol==1 and state!='E' else '')
        return compact_code

    def get_transition_info(self, symbol):
        ''' arguments: one of symbols aAbBcCdDeE
            return value: 
            symbol left behind '0' or '1',
            direction 'R' or 'L', 
            next state one of 'ABCDE' '''
        idx = 'aAbBcCdDeE'.index(symbol) * 3
        return self.shortcode[idx], self.shortcode[idx + 1], self.shortcode[idx + 2]

    def is_final(self, tm_symb):
        x, _, _ = self.get_transition_info(tm_symb)
        return x == '-'

    def final_states(self):
        return [tm_symb for tm_symb in TM.tm_symbols if self.is_final(tm_symb)]

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