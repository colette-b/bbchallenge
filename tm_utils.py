# we store everything as strings
# states = letters
# directions = 'L' or 'R'
# symbols = '0' or '1'

class TM:
    tm_symbols = 'aAbBcCdDeE'

    def __init__(self, code):
        # 1RZ has same function as ---
        self.code = code.replace('1RZ', '---')
        code_fragments = self.code.split('_')
        self.shortcode = self.code.replace('_', '')
        self.tm_symbols = ''
        for i in range(self.state_count()):
            lower = chr(ord('a') + i)
            upper = chr(ord('A') + i)
            self.tm_symbols += (lower + upper)

    def state_count(self):
        return len(self.shortcode) // 6

    def __str__(self):
        return self.code

    def get_transition_info(self, symbol):
        ''' arguments: one of symbols aAbBcCdDeE
            return value: 
            symbol left behind '0' or '1',
            direction 'R' or 'L', 
            next state one of 'ABCDE' '''
        idx = self.tm_symbols.index(symbol) * 3
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