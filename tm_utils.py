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
import math

def combo_symbol_to_char(combo_symb):
    tm_symb, tape_symb = combo_symb
    return tm_symb.lower() if tape_symb=='0' else tm_symb.upper()

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
        self.tm_states = ''.join(chr(ord('A') + i) for i in range(self.tm_state_count))
        self.tape_symbols = ''.join(chr(ord('0') + i) for i in range(self.tape_symbol_count))
        self.combo_symbols = [(tm_state, tape_symbol) for tm_state in self.tm_states for tape_symbol in self.tape_symbols]

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
        assert tm_state in self.tm_states, f'{tm_state=}'
        assert tape_symbol in self.tape_symbols
        return tm_state, tape_symbol

    def get_transition_info(self, *args):
        ''' arguments: tm_state and tape_symbol,
            return value: 
            new_tape_symbol,
            new_direction,
            new_tm_state '''
        tm_state, tape_symbol = self.parse_combo_state(*args)
        idx = self.tm_states.index(tm_state) * (3 * self.tape_symbol_count + 1) + \
                self.tape_symbols.index(tape_symbol) * 3
        return self.code[idx], self.code[idx + 1], self.code[idx + 2]

    def is_final(self, *args):
        tm_state, tape_symbol = self.parse_combo_state(*args)
        return self.get_transition_info(tm_state, tape_symbol) == ('-', '-', '-')

    def final_states(self):
        return [(tm_state, tape_symbol)
            for tm_state in self.tm_states 
            for tape_symbol in self.tape_symbols
            if self.is_final(tm_state, tape_symbol)]

    def simulation_step(self, left, combo_state, right):
        ''' right part is always reversed '''
        new_tape_symb, new_direction, new_tm_state = self.get_transition_info(combo_state)
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

    def make_image(self, pathname, width=600, height=10000, origin=0.5, _left_tape='', _right_tape='', _combo_state=('A', '0')):
        left_tape = copy.deepcopy(_left_tape)
        combo_state = copy.deepcopy(_combo_state)
        right_tape = copy.deepcopy(_right_tape)
        from PIL import Image
        img = Image.new('RGB', (width, height), color = 'black')
        pixels = img.load()
        color_map = { \
            '0': (0, 0, 0), \
            '1': (255, 255, 255), \
            '2': (128, 128, 128), \
            '3': (64, 64, 64), \
            '4': (191, 191, 191) \
        }
        letter_color_map = {
            'A': (255, 0, 0), \
            'B': (255, 127, 0), \
            'C': (0, 0, 255), \
            'D': (0, 255, 0), \
            'E': (255, 0, 255) \
        }
        alignment = math.floor(width * origin)
        for row in range(height):
            for i in range(max(0, alignment - len(left_tape)), alignment):
                pixels[i, row] = color_map[left_tape[i - alignment + len(left_tape)]]
            pixels[alignment, row] = letter_color_map[combo_state[0]]
            for i in range(alignment + 1, min(alignment + len(right_tape) + 1, width)):
                pixels[i, row] = color_map[right_tape[- i + alignment]]
            new_direction = self.get_transition_info(combo_state)[1]
            alignment += (1 if new_direction=='R' else -1)
            if self.is_final(combo_state):
                break
            left_tape, combo_state, right_tape = self.simulation_step(left_tape, combo_state, right_tape)
        img = img.resize((width, 1000), Image.NEAREST)
        img.save(pathname)

    def as_grammar_rules(self):
        rules = []
        for tm_symb, tape_symb in self.combo_symbols:
            s = tm_symb.upper() if tape_symb=='1' else tm_symb.lower()
            if self.is_final(s):
                continue
            new_bit, direction, new_tm_symb = self.get_transition_info(s)
            if direction == 'R':
                rules.append((s + '0', new_bit + new_tm_symb.lower()))
                rules.append((s + '1', new_bit + new_tm_symb.upper()))
            if direction == 'L':
                rules.append(('0' + s, new_tm_symb.lower() + new_bit))
                rules.append(('1' + s, new_tm_symb.upper() + new_bit))
        return rules

    def as_arrowed_rules(self):
        if not hasattr(self, 'rules'):
            rules = []
            for tm_symb, tape_symb in self.combo_symbols:
                if self.is_final(tm_symb, tape_symb):
                    continue
                new_bit, direction, new_tm_symb = self.get_transition_info(tm_symb, tape_symb)
                if direction == 'R':
                    res = f'{new_bit}{new_tm_symb}>'
                else:
                    res = f'<{new_tm_symb}{new_bit}'
                rules.append((f'{tm_symb}>{tape_symb}', res))
                rules.append((f'{tape_symb}<{tm_symb}', res))
            self.rules = rules
        return self.rules

    def arrowed_sim(self, s, maxsteps=10**9, break_function=lambda i, s: False):
        for i in range(maxsteps):
            if break_function(i, s):
                return
            flag = False
            for pre, res in self.as_arrowed_rules():
                if pre in s:
                    s = s.replace(pre, res)
                    flag = True
                    break
            if not flag:
                return s
