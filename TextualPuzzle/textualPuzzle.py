############################################################
# Section 1: Propositional Logic
############################################################

class Expr(object):
    def __hash__(self):
        return hash((type(self).__name__, self.hashable))

class Atom(Expr):
    def __init__(self, name):
        self.name = name
        self.hashable = name
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        # two expressions should be considered equal only if they are of the same class and have       the same internal structure
        return self.name == other.name and type(self) == type(other)
        pass

    def __repr__(self):
        return "Atom(" + self.name + ")"
        pass

    def atom_names(self):
        return {self.name}
        pass

    def evaluate(self, assignment):
        return assignment[self.name] #TRUE else FALSE
        pass

    def to_cnf(self):
        return self
        pass


class Not(Expr):
    def __init__(self, arg):
        self.arg = arg
        self.hashable = arg
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        return self.arg == other.arg and type(self) == type(other)
        pass

    def __repr__(self):
        return "Not(" + repr(self.arg) + ")"
        pass

    def atom_names(self):
        return self.arg.atom_names()
        pass

    def evaluate(self, assignment):
        return not self.arg.evaluate(assignment) #if assignment FALSE, then return TRUE
        pass

    def to_cnf(self):
        # output of this method should be a literal (i.e. an atom or a negated atom), a disjunction of literals, or a conjunction consisting of literals and/or disjunctions of literals.
        var = self.arg.to_cnf()

        if type(var) == Atom:
            return Not(var)
        if type(var) == Not:
            return var.arg
        if type(var) == And:  # DeMorgans law 1)  not (a and b) = (not a) or (not b)
            return Or(*map(Not, var.hashable))
        if type(var) == Or:  # DeMorgans law 2)  (not (a or b)) = (not a) and (not b)
            return And(*map(Not, var.hashable))
        pass
        
class And(Expr):
    def __init__(self, *conjuncts):
        self.conjuncts = frozenset(conjuncts)
        self.hashable = self.conjuncts
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        return self.conjuncts == other.conjuncts
        pass

    def __repr__(self):
        exp = ", ".join([repr(x) for x in self.hashable])
        return "And({})".format(exp)
        pass

    def atom_names(self):
        #set.union(it1, it2,...)
        return set().union(*map(lambda x: x.atom_names(), self.hashable))
        pass

    def evaluate(self, assignment):
        for x in self.hashable:
            if x.evaluate(assignment)==False:
                return False
        else: return True
        pass

    def to_cnf(self):
        temp = []
        conj = [x.to_cnf() for x in self.hashable]

        for x in conj:
            if type(x) == And:
                for i in x.hashable:
                    temp.append(i)
            else:
                temp.append(x)

        result = And(*temp)
        return result
        pass

class Or(Expr):
    def __init__(self, *disjuncts):
        self.disjuncts = frozenset(disjuncts)
        self.hashable = self.disjuncts
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        return self.disjuncts == other.disjuncts
        pass

    def __repr__(self):
        return "Or(" + ", ".join([repr(x) for x in self.hashable]) + ")"
        pass

    def atom_names(self):
        return set().union(*map(lambda x: x.atom_names(), self.hashable))
        pass

    def evaluate(self, assignment):
        for x in self.hashable:
            if x.evaluate(assignment):
                return True
        else: return False
        pass

    def to_cnf(self):
        temp = []
        conj = [x.to_cnf() for x in self.hashable]

        for x in conj:
            if type(x) == Or:
                for i in x.hashable:
                    temp.append(i)
            else:
                temp.append(x)

        in_or = Or(*temp)
        for disj in in_or.hashable:
            i = {disj}
            j = set(in_or.hashable)
            if type(disj) == And:
                # in_or(j) difference to disj(i)
                new = list(j.difference(i))
                result = And(*[Or(*([elem] + [x for x in new])).to_cnf() for elem in list(disj.hashable)]).to_cnf()
                return result

        result = Or(*temp)
        return result
        pass

class Implies(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        return self.hashable == other.hashable
        pass

    def __repr__(self):
        return "Implies(" + repr(self.left) + ", " + repr(self.right) + ")"
        pass

    def atom_names(self):
        return set().union(*map(lambda x: x.atom_names(), self.hashable))
        pass

    def evaluate(self, assignment):
        return not self.left.evaluate(assignment) or self.right.evaluate(assignment)
        pass

    def to_cnf(self):
        return Or(Not(self.left), self.right).to_cnf()
        pass

class Iff(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)
    def __hash__(self):
        return Expr.__hash__(self)
    def __eq__(self, other):
        return self.hashable == other.hashable or other.hashable == (self.right, self.left)
        pass

    def __repr__(self):
        return "Iff(" + repr(self.left) + ", " + repr(self.right) + ")"
        pass

    def atom_names(self):
        return set().union(*map(lambda x: x.atom_names(), self.hashable))
        pass

    def evaluate(self, assignment):
        return Implies(self.left, self.right).evaluate(assignment) and Implies(self.right, self.left).evaluate(assignment)
        pass

    def to_cnf(self):
        # Or(And(a,Not(b)),And(Not(a),b)) === And(Or(a,b), Or(Not(a),Not(b))
        return And(Implies(self.left, self.right), Implies(self.right, self.left)).to_cnf()
        pass

def satisfying_assignments(expr):
    # generates all assignments from atom names to  truth values
    # out of 2 to the power of n atoms, only expressions that makes it TRUE.
    # combination + permutation
    atoms = list(expr.atom_names())
    states = [True, False]
    comb = itertools.product(states, repeat=len(atoms))
    possible_dict = [{key: val for (key, val) in zip(atoms, ele)} for ele in comb]

    # check if TRUE
    for i in possible_dict:
        if expr.evaluate(i):
            yield i
    pass


class KnowledgeBase(object):
    def __init__(self):
        self.int_fact_set = set()
        pass

    def get_facts(self):
        #return an internal fact set, respectively.
        return self.int_fact_set
        pass

    def tell(self, expr):
        #converts the input expression to conjunctive normal form and adds the resulting conjuncts to the internal fact set
        self.int_fact_set.add(expr.to_cnf())
        pass

    def ask(self, expr):
        #returns a Boolean value indicating whether the facts in the knowledge base entail the input expression. Use resolution alg
        #resolution alg :
        #1) convert all to cnf.
        #2) Apply bi-cond/imp/demorg/or if applicable)
        kb = self.get_facts()
        neg = Not(expr)
        #clauses = set of clauses in the cnf rep of kb and neg(exp)
        clauses = And(*kb, neg).to_cnf()
        resolvents = list(satisfying_assignments(clauses)) #list of satisfying clauses
        if not resolvents: #if resolvents contains the empty clause return True
            return True
        return False
        pass
