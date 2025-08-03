from collections import defaultdict
import itertools
import copy

class Sentence():
    """ A logic sentence """
    def evaluate(self, model):
        """Evaluates the logical sentence."""
        raise Exception("nothing to evaluate")

    def formula(self):
        """Returns string formula representing logical sentence."""
        return ""

    def symbols(self):
        """Returns a set of all symbols in the logical sentence."""
        return set()

    @classmethod
    def validate(cls, sentence):
        """ Determine if the object is a sentence """
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, string):
        """Parenthesizes an expression if not already parenthesized."""
        def balanced(string):
            """Checks if a string has balanced parentheses."""
            count = 0
            for char in string:
                if char == "(":
                    count += 1
                elif char == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if len(string) == 0 or string.isalpha() or (
            string[0] == "(" and string[-1] == ")" and balanced(string[1:-1])
        ):
            return string

        return f"({string})"


class Symbol(Sentence):
    """ Logic symbols """
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def __repr__(self):
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}


class Not(Sentence):
    """ Logic connective NOT """
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def __repr__(self):
        return f"Not({self.operand})"

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()

class And(Sentence):
    """ Logic connective AND """
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(
            ("and", tuple(hash(conjunct) for conjunct in self.conjuncts))
        )

    def __repr__(self):
        conjunctions = ", ".join(
            [str(conjunct) for conjunct in self.conjuncts]
        )
        return f"And({conjunctions})"

    def add(self, conjunct):
        """ Link two set of sentences with and junction """
        Sentence.validate(conjunct)
        conjunct = to_cnf(conjunct)
        if isinstance(conjunct, And):
            self.conjuncts.extend(conjunct.conjuncts)
        else:
            self.conjuncts.append(conjunct)

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula())
                           for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])


class Or(Sentence):
    """ Logic connective OR """
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(
            ("or", tuple(hash(disjunct) for disjunct in self.disjuncts))
        )

    def __repr__(self):
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"
    
    def add(self, disjunct):
        """ Link two set of sentences with and junction """
        Sentence.validate(disjunct)
        self.disjuncts.append(disjunct)

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨  ".join([Sentence.parenthesize(disjunct.formula())
                            for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])

class Implication(Sentence):
    """ Logic connective Implication """
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication)
                and self.antecedent == other.antecedent
                and self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        return ((not self.antecedent.evaluate(model))
                or self.consequent.evaluate(model))

    def formula(self):
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())


class Biconditional(Sentence):
    """ Logic connective Biconditional """
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (isinstance(other, Biconditional)
                and self.left == other.left
                and self.right == other.right)

    def __hash__(self):
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        return ((self.left.evaluate(model)
                 and self.right.evaluate(model))
                or (not self.left.evaluate(model)
                    and not self.right.evaluate(model)))

    def formula(self):
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())



def forward_chaining(kb, query):
    # get facts (not including 'negative fact')
    facts = [clause for clause in kb.clauses.conjuncts if isinstance(clause, Symbol)]
    inferred = defaultdict(bool)
    # dict -> the number symbol in premise
    count = dict()
    for c in kb.clauses.conjuncts:
        if isinstance(c, Implication):
            if isinstance(c.antecedent, And):
                count[c] = len(c.antecedent.conjuncts)
            else:
                count[c] = 1

    # rules = kb_with_premise(kb.clauses)
    while facts:
        fact = facts.pop()
        print(fact)
        if fact == query:
            return True
        if not inferred[fact]:
            inferred[fact] = True
            for rule in kb.list_clauses_with_premise(fact):
                print(f'rule: {rule}')
                count[rule] -= 1
                if count[rule] == 0:
                    facts.append(rule.consequent)
    return False


def model_check(kb, query):
    """Checks if knowledge base entails query."""
    knowledge = kb.clauses
    def check_all(knowledge, query, symbols, model):
        """Checks if knowledge base entails query, given a particular model."""

        # If model has an assignment for each symbol
        if not symbols:

            # If knowledge base is true in model, then query must also be true
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:

            # Choose one of the remaining unused symbols
            remaining = symbols.copy()
            top = remaining.pop()

            # Create a model where the symbol is true
            model_true = model.copy()
            model_true[top] = True

            # Create a model where the symbol is false
            model_false = model.copy()
            model_false[top] = False

            # Ensure entailment holds in both models
            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    # Get all symbols in both knowledge and query
    symbols = set.union(knowledge.symbols(), query.symbols())
    # Check that knowledge entails query
    return check_all(knowledge, query, symbols, dict())



def move_forward(step):
    return Symbol(f'MoveForward_{step}')


def shoot(from_location, direction, step):
    y, x = from_location[:2]
    return Symbol(f'ShootFrom_{y}_{x}_{direction}_{step}')

def grab(from_location, step):
    y, x = from_location[:2]
    return Symbol(f'Grab_{y}_{x}_{step}')
# def turn_left(from_location):
#     y, x = from_location[:2]
#     return Symbol(f'TurnLeft_{y}_{x}')
def turn_left(step):
    return Symbol(f'TurnLeft_{step}')


# def turn_right(from_location):
#     y, x = from_location[:2]
#     return Symbol(f'TurnRight_{y}_{x}')
def turn_right(step):
    return Symbol(f'TurnRight_{step}')


def ok_to_move(x, y):
    return Symbol(f'OK_{y}_{x}')

def flatten_or(sent):
    """Recursively flatten nested Or operations."""
    if isinstance(sent, Or):
        flat_disjuncts = []
        for d in sent.disjuncts:
            d = flatten_or(d)
            if isinstance(d, Or):
                flat_disjuncts.extend(d.disjuncts)
            else:
                flat_disjuncts.append(d)
        return Or(*flat_disjuncts)
    elif isinstance(sent, And):
        return And(*[flatten_or(c) for c in sent.conjuncts])
    elif isinstance(sent, Not):
        return Not(flatten_or(sent.operand))
    return sent


def to_cnf(sentence):
    """Convert a logical sentence to Conjunctive Normal Form (CNF), flattening nested Or operations."""
    
    def eliminate_implications(sent):
        if isinstance(sent, Implication):
            antecedent = eliminate_implications(sent.antecedent)
            consequent = eliminate_implications(sent.consequent)
            return Or(Not(antecedent), consequent)
        elif isinstance(sent, Biconditional):
            left = eliminate_implications(sent.left)
            right = eliminate_implications(sent.right)
            return And(Or(Not(left), right), Or(Not(right), left))
        elif hasattr(sent, 'conjuncts'):
            return And(*[eliminate_implications(c) for c in sent.conjuncts])
        elif hasattr(sent, 'disjuncts'):
            return Or(*[eliminate_implications(d) for d in sent.disjuncts])
        elif isinstance(sent, Not):
            operand = eliminate_implications(sent.operand)
            return Not(operand)
        return sent

    def move_not_inwards(sent):
        if isinstance(sent, Not):
            operand = sent.operand
            if isinstance(operand, Not):
                return move_not_inwards(operand.operand)
            elif isinstance(operand, And):
                return Or(*[move_not_inwards(Not(c)) for c in operand.conjuncts])
            elif isinstance(operand, Or):
                return And(*[move_not_inwards(Not(d)) for d in operand.disjuncts])
            return sent
        elif hasattr(sent, 'conjuncts'):
            return And(*[move_not_inwards(c) for c in sent.conjuncts])
        elif hasattr(sent, 'disjuncts'):
            return Or(*[move_not_inwards(d) for d in sent.disjuncts])
        return sent

    def distribute_or_over_and(sent):
        """Distribute OR over AND to convert to CNF."""
        if isinstance(sent, Symbol) or (isinstance(sent, Not) and isinstance(sent.operand, Symbol)):
            return sent
        if isinstance(sent, Or):
            disjuncts = [distribute_or_over_and(d) for d in sent.disjuncts]
            and_clauses = [d for d in disjuncts if isinstance(d, And)]
            if not and_clauses:
                return Or(*disjuncts)
            if len(and_clauses) > 1:
                raise ValueError("Multiple And clauses in Or not supported yet")
            base_and = and_clauses[0]
            other_disjuncts = [d for d in disjuncts if d != base_and]
            return And(*[Or(*[distribute_or_over_and(c)] + other_disjuncts)
                         for c in base_and.conjuncts])
        elif isinstance(sent, And):
            return And(*[distribute_or_over_and(c) for c in sent.conjuncts])
        return sent

    # Step-by-step conversion with flattening
    sent = flatten_or(sentence)  # Flatten input
    sent = eliminate_implications(sent)
    sent = flatten_or(sent)  # Flatten after implications
    sent = move_not_inwards(sent)
    sent = flatten_or(sent)  # Flatten after negations
    sent = distribute_or_over_and(sent)
    sent = flatten_or(sent)  # Flatten final result
    return sent


def pl_resolution(kb, query):
    """Implement resolution refutation to check if kb |= alpha."""
    # Convert kb and ¬alpha to CNF
    # newkb = copy.deepcopy(kb)
    # newkb.clauses.add(Not(alpha))
    # print(newKB.clauses.formula())
    clauses = kb.clauses.conjuncts.copy()
    negate_query = Not(query)
    clauses.append(negate_query)
    # print(clauses)
    new = set()

    while True:
    # for i in range(2):
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        # print(f'pairs:{pairs}')
        # print()
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
            # print(f'new:{new}')
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)
        # print(clauses)
        
    

# def pl_resolve(Ci, Cj):
    # print(f'ci:{Ci}')
#     print(f'cj:{Cj}')
#     print()
#     """Resolve two clauses to produce resolvents."""
#     resolvents = set()
#     # Simple resolution (assuming binary resolution for now)
#     if isinstance(Ci, Or) and isinstance(Cj, Or):
#         for li in Ci.disjuncts:
#             for lj in Cj.disjuncts:
#                 if isinstance(li, Not) and isinstance(lj, Symbol) and li.operand == lj:
#                     resolvents.add(Cj)
#                 elif isinstance(lj, Not) and isinstance(li, Symbol) and lj.operand == li:
#                     resolvents.add(Ci)
#     return list(resolvents)
def pl_resolve(ci, cj):
    """Return all resolvent clauses from resolving ci and cj."""
    resolvents = []

    # Get disjuncts from both ci and cj
    # if isinstance(ci, Or):
        # print(f'OR: {ci.disjuncts}')
    disjuncts_ci = ci.disjuncts if isinstance(ci, Or) else [ci]
    disjuncts_cj = cj.disjuncts if isinstance(cj, Or) else [cj]

    # print('-')
    # print(f'disjucts_ci:{disjuncts_ci}')
    # print(f'disjucts_cj:{disjuncts_cj}')
    # print('-')

    for di in disjuncts_ci:
        for dj in disjuncts_cj:
            # Check if di and dj are complementary
            # print(f'1: {di} and {dj}')
            # print('___')
            # print('___')
            if (isinstance(di, Not) and di.operand == dj) or (isinstance(dj, Not) and dj.operand == di):
                # print(f'2: {di} and {dj}')
                # Remove di and dj
                # print(f'disjuncts_cj:{disjuncts_cj}')
                # print(f'disjuncts_ci:{disjuncts_ci}')
                
                rest_di = [d for d in disjuncts_ci if d != di]
                rest_dj = [d for d in disjuncts_cj if d != dj]
                # print(f'disjuncts_cj_after:{rest_dj}')
                # print(f'disjuncts_ci_after:{rest_di}')
                combined = rest_di + rest_dj
                # print(combined)

                # Remove duplicates
                unique_literals = []
                for lit in combined:
                    if lit not in unique_literals:
                        unique_literals.append(lit)
                # print(f'unique:{unique_literals}')
                # If nothing left => empty clause (contradiction)
                if len(unique_literals) == 0:
                    # print(f'3: {di} and {dj}')
                    return [False]  # Representing contradiction

                # Otherwise, return new clause (Or if multiple, else single literal)
                if len(unique_literals) == 1:
                    resolvents.append(unique_literals[0])
                else:
                    resolvents.append(Or(*unique_literals))

    return flatten_or(resolvents)