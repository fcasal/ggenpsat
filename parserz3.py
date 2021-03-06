'''parsing functions based on Norvig's http://norvig.com/lispy.html'''

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


class translation:

    def __init__(self):
        self.insidepr = []
        self.gamma = []
        self.ghosts = dict()
        self.atlas = dict() #vars alphapsi_i
        self.prtolira = []
        self.probform = []
        self.int_vars = []
        self.real_vars = []
        self.bool_vars = []
        self.final = "(set-option :timeout 120000)\n"

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

    def build_and_declare(self):
        self.insidepr = list(set(self.insidepr))
        self.gamma = list(set(self.gamma))
        self.relf = list(set(self.gamma + self.insidepr))

        i = 0
        for form in self.relf:
            self.atlas[form] = 'apsi' + str(i)
            self.final += '(declare-const '+ self.atlas[form] +' Real)\n'
            self.final += '(assert (and (<= '+ self.atlas[form] +' 1) (>= '+ self.atlas[form] +' 0)))\n'

            self.ghosts[form] = 'gh' + str(i)
            i += 1

        # build B set
        self.b = self.ghosts.values()
        self.bcopies = [map(lambda x:  x + '@' + str(i), self.b) for i in range(1, len(self.atlas.values()) + 2 )]
        self.bool_vars_copies = [map(lambda x:  x + '@' + str(i), self.bool_vars) for i in range(1, len(self.atlas.values()) + 2 )]
        aux = [item for sublist in self.bcopies for item in sublist]
        for ghost in aux:
            self.final += '(declare-const '+ ghost +' Bool)\n'

        aux = [item for sublist in self.bool_vars_copies for item in sublist]

        for ghost in aux:
            self.final += '(declare-const '+ ghost +' Bool)\n'
        sizeG = len(self.relf)

        self.hvars = [["h"+str(i)+"@"+str(j) for j in range(sizeG + 1)] for i in range(sizeG)]
        self.bvars = [["b"+str(i)+"@"+str(j) for j in range(sizeG + 1)] for i in range(sizeG)]
        self.pivars = ['pi' + str(j) for j in range(sizeG + 1)]

        for i in range(sizeG):
            for j in range(sizeG + 1):
                self.final += '(declare-const '+ self.hvars[i][j] +' Int)\n'
                self.final += '(assert (or (= '+ self.hvars[i][j] +' 1) (= '+ self.hvars[i][j] +' 0)))\n'

                self.final += '(declare-const '+ self.bvars[i][j] +' Real)\n'
                self.final += '(assert (and (<= '+ self.bvars[i][j] +' 1) (>= '+ self.bvars[i][j] +' 0)))\n'
            self.final += '(declare-const ' + self.pivars[i] + ' Real)\n'
            self.final += '(assert (and (<= '+ self.pivars[i] +' 1) (>= '+ self.pivars[i] +' 0)))\n'
        self.final += '(declare-const ' + self.pivars[sizeG] + ' Real)\n'
        self.final += '(assert (and (<= '+ self.pivars[sizeG] +' 1) (>= '+ self.pivars[sizeG] +' 0)))\n'

        for i in range(sizeG):
            # val1 restriction
            self.final += '(assert (= (+ ' + ' '.join(self.bvars[i]) + ') '+ self.atlas[self.relf[i]] +'))\n'
            # prop_prob restriction
            for k in range(sizeG + 1):
                aux = self.relf[i]
                for idx, var in enumerate(self.bool_vars_copies[k]):
                    if (' '+self.bool_vars[idx]+' ' in aux) or (' '+self.bool_vars[idx]+ ')' in aux):
                        aux = aux.replace(' ' + self.bool_vars[idx] + ' ', ' '+var+ ' ')
                        aux = aux.replace(' '+self.bool_vars[idx]+ ')', ' '+var+ ')')
                    if self.bool_vars[idx] == aux:
                        aux = aux.replace(self.bool_vars[idx], var)
                self.final += '(assert (and (=> {} {}) (=> {} {})))\n'.format(self.bcopies[k][i], aux, aux, self.bcopies[k][i])

            for j in range(sizeG + 1):
                # cons restriction
                self.final += '(assert (and (=> (= {} 1) {}) (=> {} (= {} 1))))\n'.format(self.hvars[i][j], self.bcopies[j][i], \
                                    self.bcopies[j][i], self.hvars[i][j])
                # val2 restriction
                self.final += '(assert (<= 0 {}))\n'.format(self.bvars[i][j])
                self.final += '(assert (<= {} {}))\n'.format(self.bvars[i][j], self.hvars[i][j])
                self.final += '(assert (<= (+ {} {} -1) {}))\n'.format(self.hvars[i][j], self.pivars[j], self.bvars[i][j])
                self.final += '(assert (<= {} {}))\n'.format(self.bvars[i][j], self.pivars[j])
        # sums1 restriction
        self.final += '(assert (= (+ {}) 1))\n'.format(" ".join(self.pivars))

    def PrToLIRA(self):
        for form in self.probform:
            for psi in self.insidepr:
                if '(pr ' + psi + ')' in form:
                    # print(form)
                    form = form.replace('(pr ' + psi + ')', self.atlas.get(psi, None))
            self.prtolira += [form]
        s = " ".join(self.prtolira)
        form = '(assert (and {}))\n'.format(s)
        self.final += form

    def hard_constr(self):
        l = [self.atlas.get(form, None) for form in self.gamma]
        if l != []:
            l = map(lambda s: '(= ' + s + ' 1)', l)
            s = " ".join(l)
            form = '(assert (and {}))\n'.format(s)
            self.final += form

    def finalize(self, filename):
        self.final += '(check-sat)'
        # self.final += '\n(show-model)'
        with open(filename, 'w+') as f:
            f.write(self.final)

    def begin(self, filename):
        with open(filename) as fp:
            for line in fp:
                self.eval(parse(line))

def ggenpsat(iname, oname = None):
    p = translation()
    p.begin(iname)
    p.build_and_declare()
    # p.show()
    p.PrToLIRA()
    p.hard_constr()
    if oname == None:
        p.finalize('z3ans_' + iname)
    else:
        p.finalize(oname)
