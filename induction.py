import copy

class Token:
    def __init__(self, text, kind):
        self.text = text
        self.kind = kind

    def __repr__(self):
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    def chg_offset(self, chg):
        return self

    def instantiate(self, n):
        return self.text

class BasicToken(Token):
    def __init__(self, char):
        super().__init__(char, 'basic')

class ComboToken(Token):
    def __init__(self, word, n_offset):
        if n_offset == 0:
            offset_str = ''
        else:
            offset_str = f'+{n_offset}' if n_offset > 0 else f'{n_offset}'
        super().__init__(f'({word})^(n{offset_str})', 'combo')
        self.word = word
        self.n_offset = n_offset

    def chg_offset(self, chg):
        return ComboToken(self.word, self.n_offset + chg)

    def instantiate(self, n):
        assert(n + self.n_offset >= 0)
        return self.word * (n + self.n_offset)

class TokenSeq:
    def __init__(self, seq):
        assert(type(seq) is list)
        self.seq = seq
    
    def __len__(self):
        return len(self.seq)
    
    def __add__(self, other):
        assert(type(other) is TokenSeq)
        return TokenSeq(self.seq + other.seq)

    def __eq__(self, other):
        if type(other) is not TokenSeq:
            return False
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __getitem__(self, idx):
        if type(idx) is int:
            return self.seq[idx]
        if type(idx) is slice:
            return TokenSeq(self.seq[idx])
        assert(False)

    def findall(self, other):
        pos = []
        assert(type(other) is TokenSeq)
        for i in range(0, len(self) - len(other) + 1):
            if self[i: i + len(other)] == other:
                pos.append(i)
        return pos

    def rule_yield(self, rule):
        for pos in self.findall(rule.pre):
            yield self[:pos] + rule.post + self[pos + len(rule.pre):]

    def __contains__(self, other):
        return len(self.findall(other)) > 0

    def __repr__(self):
        return ' '.join(str(token) for token in self.seq)

    def __hash__(self):
        return hash(self.__repr__())

    def chg_offset(self, chg):
        return TokenSeq([token.chg_offset(chg) for token in self.seq])

    def minimal_valid_n(self):
        return max((0,) + tuple(-token.n_offset for token in self if type(token) is ComboToken))

    def instantiate(self, n):
        assert(n >= self.minimal_valid_n())
        return ''.join(token.instantiate(n) for token in self)

class Rule:
    def __init__(self, pre, post):
        self.pre = pre
        self.post = post
        if type(self.pre) is list:
            self.pre = TokenSeq(self.pre)
        if type(self.post) is list:
            self.post = TokenSeq(self.post)
    
    def __repr__(self):
        return str(self.pre) + ' -> ' + str(self.post)

    def chg_offset(self, chg):
        return Rule(self.pre.chg_offset(chg), self.post.chg_offset(chg))

    def minimal_valid_n(self):
        return max(self.pre.minimal_valid_n(), self.post.minimal_valid_n())

    def instantiate(self, n):
        return Rule(self.pre.instantiate(n), self.post.instantiate(n))

    def test_for_value(self, n, tm):
        rule_to_test = self.instantiate(n)
        class FlagClass:
            def __init__(self):
                self.flag = False
            
            def bf(self, i, s):
                if s == rule_to_test.post:
                    self.flag = True
                    return True
                return False
        fc = FlagClass()
        tm.arrowed_sim(rule_to_test.pre, break_function=fc.bf)
        return fc.flag

def tm_rules(tm):
    rules = []
    for pre_, post_ in tm.as_arrowed_rules():
        pre = TokenSeq([BasicToken(pre_[0]), BasicToken(pre_[1]), BasicToken(pre_[2])])
        post = TokenSeq([BasicToken(post_[0]), BasicToken(post_[1]), BasicToken(post_[2])])
        rules.append(Rule(pre, post))
    return rules

def word_rules(w, lo, hi):
    rules = []
    wseq = [BasicToken(ch) for ch in w]
    # extracting or inserting one copy of a word
    for i in range(lo, hi):
        rules.append(Rule([ComboToken(w, i + 1)], [ComboToken(w, i)] + wseq))
        rules.append(Rule([ComboToken(w, i + 1)], wseq + [ComboToken(w, i)]))
        rules.append(Rule([ComboToken(w, i)] + wseq, [ComboToken(w, i + 1)]))
        rules.append(Rule(wseq + [ComboToken(w, i)], [ComboToken(w, i + 1)]))
    # cyclic shift rule
    for i in range(lo, hi + 1):
        rules.append(Rule(
            [ComboToken(w, i), BasicToken(w[0])],
            [BasicToken(w[0]), ComboToken(w[1:] + w[0], i)]
        ))
        rules.append(Rule(
            [BasicToken(w[0]), ComboToken(w[1:] + w[0], i)],
            [ComboToken(w, i), BasicToken(w[0])]
        ))
    return rules

def word_rules_full(w, lo, hi):
    rules = []
    for i in range(len(w)):
        rules += word_rules(w[i:] + w[:i], lo, hi)
    return rules

class Proof:
    def __init__(self, words, rules):
        assert(len(words) == len(rules))
        self.words = words
        self.rules = rules
        
    def __repr__(self):
        s = f'==== proof of length {len(self.words)} ====\n'
        for word, rule in zip(self.words, self.rules):
            s += f'{str(word):50}{str(rule)}\n'
        return s

def look_for_derivation(start, target, rules, maxsteps=20, verbose=False):
    wordsets = [{start: (None, 'start')}]
    for i in range(maxsteps):
        new_wordset = dict()
        for word in wordsets[i]:
            for rule in rules:
                for newword in word.rule_yield(rule):
                    new_wordset[newword] = (word, rule)
        wordsets.append(new_wordset)
        if target in new_wordset:
            ''' retrieve a proof '''
            cur_word = target
            proof_words, proof_rules = [], []
            for j in reversed(range(i + 2)):
                proof_words.append(cur_word)
                proof_rules.append(wordsets[j][cur_word][1])
                cur_word = wordsets[j][cur_word][0]
            return Proof(list(reversed(proof_words)), list(reversed(proof_rules)))
        if verbose:
            print(i + 1, len(new_wordset))
    return None

