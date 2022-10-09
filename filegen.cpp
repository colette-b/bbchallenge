#include <bits/stdc++.h>

using namespace std;
vector<char> tm_symbols = {'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E'};
map<char, int> symb_idx = {
    {'a', 0},
    {'A', 3},
    {'b', 7},
    {'B', 10},
    {'c', 14},
    {'C', 17},
    {'d', 21},
    {'D', 24},
    {'e', 28},
    {'E', 31}
};

bool is_final_(string tm_code, char tm_symb) {
    return tm_code[symb_idx[tm_symb]] == '-';
}

void instance_gen(string tm_code, int n) {
    for(int b = 0; b <= 1; b++) {
        for(int i = 0; i < n; i++) {
            for(int j = 0; j < n; j++) {
                printf("(declare-fun tr_%d_%d_%d () Bool)\n", i, j, b);
                printf("(declare-fun tr_%d_%d_%d () Bool)\n", i + n, j + n, b);
            }
        }
    }
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n; j++) {
            for(auto s : tm_symbols) {
                printf("(declare-fun acc_%d_%d_%c () Bool)\n", i, j + n, s);
            }
        }
    }
    for(int b = 1; b <= 2; b++) {
        for(int i = 0; i < n; i++) {
            for(int t = -1; t < 2*n; t++) {
                printf("(declare-fun r%d_%d_%d () Bool)\n", b, b==1 ? i : i + n, t);
            }
        }
    }
    for(int b = 0; b <= 1; b++) {
        for(int i = 0; i < 2*n; i++) {
            printf("(assert\n  ((_ pbeq ");
            for(int _ = 0; _ <= n; _++)
                printf(_<n ? "1 " : "1) ");
            for(int j = 0; j < n; j++) {
                printf("tr_%d_%d_%d", i, j + (i>=n ? n : 0), b);
                printf(j<n-1 ? " " : "))\n");
            }
        }
    }
    printf("(assert\n (= acc_0_%d_a true))\n", n);
    printf("(assert\n (= tr_0_0_0 true))\n");
    printf("(assert\n (= tr_%d_%d_0 true))\n", n, n);
    int ctr = 4;
    for(auto s : tm_symbols) {
        char new_bit = tm_code[symb_idx[s] + 0];
        char direction = tm_code[symb_idx[s] + 1];
        char new_tm_symb = tm_code[symb_idx[s] + 2];
        for(int p_ = 0; p_ < n; p_++) {
            for(int p = 0; p < n; p++) {
                for(int q = n; q < 2*n; q++) {
                    for(int q_ = n; q_ < 2*n; q_++) {
                        for(int b = 0; b <= 1; b++) {
                            if(direction == 'R') {
                                printf("(assert\n (let (($x%d (and tr_%d_%d_%d acc_%d_%d_%c tr_%d_%d_%c)))\n (=> $x%d acc_%d_%d_%c)))\n",
                                    ctr,
                                    q_, q, b,
                                    p_, q, s,
                                    p_, p, new_bit,
                                    ctr += 4,
                                    p, q_, b==0 ? tolower(new_tm_symb) : toupper(new_tm_symb));
                            }
                            if(direction == 'L') {
                                printf("(assert\n (let (($x%d (and tr_%d_%d_%d acc_%d_%d_%c tr_%d_%d_%c)))\n (=> $x%d acc_%d_%d_%c)))\n",
                                    ctr,
                                    p_, p, b,
                                    p, q_, s,
                                    q_, q, new_bit,
                                    ctr += 4,
                                    p_, q, b==0 ? tolower(new_tm_symb) : toupper(new_tm_symb));
                            }
                        }
                    }
                }
            }
        }
    }
    for(char s : tm_symbols) {
        if(is_final_(tm_code, s)) {
            for(int i = 0; i < n; i++) {
                for(int j = n; j < 2*n; j++) {
                    printf("(assert\n (= acc_%d_%d_%c false))\n", i, j, s);
                }
            }
        }
    }
    for(int c = 0; c <= 1; c++) {
        int offset = (c==0 ? 0 : n);
        for(int i = 0; i < n; i++) {
            printf("(assert\n (= r%d_%d_-1 %s))\n", c + 1, i + offset, i==0 ? "true" : "false");
        }
        for(int i = 0; i < n - 1; i++) {
            for(int t = -1; t < 2*n; t++) {
                printf("(assert\n (=> r%d_%d_%d r%d_%d_%d))\n", c + 1, i + offset + 1, t, c + 1, i + offset, t);
            }
        }
        for(int i = 0; i < n; i++) {
            for(int t = -1; t < 2*n - 1; t++) {
                printf("(assert\n (= r%d_%d_%d (or r%d_%d_%d (and r%d_%d_%d tr_%d_%d_%d))))\n",
                    c + 1, i + offset, t + 1,
                    c + 1, i + offset, t,
                    c + 1, t / 2 + offset, t,
                    t / 2 + offset, i + offset, (t+2) % 2
                );
            }
        }
    }
    printf("(check-sat)\n");
}

int main(int argc, char** argv) {
    assert(argc == 3);
    int n = atoi(argv[1]);
    string tm_code(argv[2]);
    instance_gen(tm_code, n);
}
