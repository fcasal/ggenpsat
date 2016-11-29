#

def tokenize(chars):
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    "Read a Scheme expression from a string."
    if program.strip() != "":
        return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token) #Symbol(token)

def schemestr(exp):
    "Convert a Python object back into a Scheme-readable string."
    if  isinstance(exp, list):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


class parser:

    def __init__(self):
        self.insidepr = []
        self.gamma = []
        self.atlas = dict()
        self.prtolira = []
        self.probform = []
        self.int_vars = []
        self.real_vars = []
        self.bool_vars = []

    def eval(self, x):
        "Evaluate an expression."
        if isinstance(x, str):      # variable reference
            pass
        elif not isinstance(x, list):  # constant literal
            pass
        elif x[0] == 'pr':          # (probability exp)
            (_, exp) = x
            exp = schemestr(exp)
            self.insidepr += [exp]
        elif x[0] == 'assertprop':
            (_, exp) = x
            exp = schemestr(exp)
            self.gamma += [exp]
        elif x[0] == 'assert':
            (_, exp) = x
            exp = schemestr(exp)
            self.probform += [exp]
            [self.eval(arg) for arg in x[1:]]
        elif x[0] == 'define':         # (define var::type)
            (_, exp) = x
            name, dom = exp.split("::")
            if dom == "int":
                self.int_vars += [name]
            elif dom == "real":
                self.real_vars += [name]
            elif dom == "bool":
                self.bool_vars += [name]
            else:
                raise("dont know type " + dom)
        else:                          # (proc arg...)
            [self.eval(arg) for arg in x[1:]]
            pass

    def show(self):
        if self.insidepr:
            print("\nInsidePr = " + str(self.insidepr))
        if self.gamma:
            print("\nGamma = " + str(self.gamma))
        if self.probform:
            print("\nProbformulass = " + str(self.probform))
        if self.bool_vars:
            print("\nBool variables = " + str(self.bool_vars))
        if self.int_vars:
            print("\nInt variables = " + str(self.int_vars))
        if self.real_vars:
            print("\nReal variables = " + str(self.real_vars))

    def build_relf(self):
        self.insidepr = list(set(self.insidepr))
        self.relf = list(set(self.gamma + self.insidepr))
        print(self.relf)
        i = 0
        for form in self.relf:
            self.atlas[form] = 'apsi' + str(i)
            i += 1

    def PrToLIRA(self):
        for form in self.probform:
            for psi in self.insidepr:
                if '(pr ' + psi + ')' in form:
                    upd = form.replace('(pr ' + psi + ')', self.atlas.get(psi, None))
                    self.prtolira += [upd]
                    # update prtolira set

    def hard_constr(self):
        l = [self.atlas.get(form, None) for form in self.gamma]
        print(" ".join(l))

p = parser()

# loc = "(assert (= (pr (not (and (=> (xor x y) x) (=> x (xor x y))))) (/ 1 2)))"
# parsed = parse(loc)
# print(parsed)
# print(schemestr(parsed))
# p.eval(parsed)
#
# print("\n/**********************/\n")
# loc = "(assert (or (= (pr x) 0) (= (pr x) 1)))"
# parsed = parse(loc)
# print(parsed)
# print(schemestr(parsed))
# p.eval(parsed)
#
# print("\n/**********************/\n")
# loc = "(define y::bool)"
# parsed = parse(loc)
# print(parsed)
# print(schemestr(parsed))
# p.eval(parsed)
#
# print("\n/**********************/\n")
# p.show()
#

with open('ex1') as fp:
    for line in fp:
        # print(line)
        p.eval(parse(line))

p.show()
p.build_relf()
p.PrToLIRA()
p.hard_constr()
