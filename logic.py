class Sentence:
    def evaluate(self, model):
        raise Exception("nothing to evaluate")

    def formula(self):
        return ""

    def symbols(self):
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, string):
        def balanced(string):
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
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(("and", tuple(hash(conjunct) for conjunct in self.conjuncts)))

    def __repr__(self):
        conjunctions = ", ".join([str(conjunct) for conjunct in self.conjuncts])
        return f"And({conjunctions})"

    def add(self, conjunct):
        Sentence.validate(conjunct)
        conjunct = to_cnf(conjunct)
        if conjunct in self.conjuncts:
            return
        if isinstance(conjunct, And):
            self.conjuncts.extend(conjunct.conjuncts)
        else:
            self.conjuncts.append(conjunct)

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " \n ".join([Sentence.parenthesize(conjunct.formula()) for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])

class Or(Sentence):
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(("or", tuple(hash(disjunct) for disjunct in self.disjuncts)))

    def __repr__(self):
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"

    def add(self, disjunct):
        Sentence.validate(disjunct)
        self.disjuncts.append(disjunct)

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨ ".join([Sentence.parenthesize(disjunct.formula()) for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])

class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication) and
                self.antecedent == other.antecedent and
                self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def formula(self):
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())

class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (isinstance(other, Biconditional) and
                self.left == other.left and
                self.right == other.right)

    def __hash__(self):
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        return ((self.left.evaluate(model) and self.right.evaluate(model)) or
                (not self.left.evaluate(model) and not self.right.evaluate(model)))

    def formula(self):
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())

def move_forward(step):
    return Symbol(f'MoveForward_{step}')

def shoot(from_location, direction, step):
    y, x = from_location[:2]
    return Symbol(f'ShootFrom_{y}_{x}_{direction}_{step}')

def grab(from_location, step):
    y, x = from_location[:2]
    return Symbol(f'Grab_{y}_{x}_{step}')

def turn_left(step):
    return Symbol(f'TurnLeft_{step}')

def turn_right(step):
    return Symbol(f'TurnRight_{step}')

def ok_to_move(x, y):
    return Symbol(f'OK_{y}_{x}')

def flatten_or(sent):
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

    sent = flatten_or(sentence)
    sent = eliminate_implications(sent)
    sent = flatten_or(sent)
    sent = move_not_inwards(sent)
    sent = flatten_or(sent)
    sent = distribute_or_over_and(sent)
    sent = flatten_or(sent)
    return sent

def negation(literal):
    if isinstance(literal, Symbol):
        return Not(literal)
    elif isinstance(literal, Not):
        return literal.operand
    else:
        raise ValueError("Invalid literal")

# def get_literals(clause):
#     if isinstance(clause, Or):
#         return clause.disjuncts
#     elif isinstance(clause, (Symbol, Not)):
#         return [clause]
#     return []


# def simplify_kb_with_unit(kb, unit):
#     negation_unit = negation(unit)
#     new_clauses = []
#     for clause in kb.clauses.conjuncts:
#         literals = get_literals(clause)
#         if unit in literals:
#             continue
#         elif negation_unit in literals:
#             new_literals = [lit for lit in literals if lit != negation_unit]
#             if new_literals:
#                 new_clause = Or(*new_literals) if len(new_literals) > 1 else new_literals[0]
#                 if not is_tautology(new_clause):
#                     new_clauses.append(new_clause)
#         else:
#             if not is_tautology(clause):
#                 new_clauses.append(clause)
#     if unit not in new_clauses:
#         new_clauses.append(unit)
#     unique_clauses = []
#     seen = set()
    # for clause in new_clauses:
    #     clause_str = clause.formula()
    #     if clause_str not in seen:
    #         seen.add(clause_str)
    #         unique_clauses.append(clause)
    # kb.clauses = And(*unique_clauses)

def normalize_clause(clause):
    if clause is False:
        return False
    if isinstance(clause, Or):
        sorted_disjuncts = sorted(clause.disjuncts, key=lambda x: x.formula())
        return Or(*sorted_disjuncts)
    if isinstance(clause, Symbol) or isinstance(clause, Not):
        return clause
    raise ValueError(f"Unexpected clause type: {type(clause)}")
def is_tautology(clause):
    """Check if a clause is a tautology (e.g., A ∨ ¬A)."""
    if isinstance(clause, Or):
        literals = set(lit.formula() for lit in clause.disjuncts)
        for lit in clause.disjuncts:
            if isinstance(lit, Symbol) and f"¬{lit.formula()}" in literals:
                return True
            if isinstance(lit, Not) and lit.operand.formula() in literals:
                return True
    return False

def simplify_clause(clause, unit_clauses):
    """Simplify a clause using unit clauses, ensuring proper propagation."""
    if isinstance(clause, Or):
        literals = [lit for lit in clause.disjuncts]
        for unit in unit_clauses:
            neg_unit = negation(unit)
            if unit in literals:
                return None  # Clause is satisfied (e.g., unit is true)
            if neg_unit in literals:
                literals = [lit for lit in literals if lit != neg_unit]
        if not literals:
            return False  # Clause is contradicted
        return Or(*literals) if len(literals) > 1 else literals[0]
    elif isinstance(clause, (Symbol, Not)):
        neg_clause = negation(clause)
        if clause in unit_clauses:
            return None  # Clause is satisfied
        if neg_clause in unit_clauses:
            return False  # Clause is contradicted
        return clause
    return clause

def pl_resolve(ci, cj):
    """Resolve two clauses, returning a list of resolvents."""
    resolvents = []
    disjuncts_ci = ci.disjuncts if isinstance(ci, Or) else [ci]
    disjuncts_cj = cj.disjuncts if isinstance(cj, Or) else [cj]
    for di in disjuncts_ci:
        for dj in disjuncts_cj:
            if (isinstance(di, Not) and di.operand == dj) or (isinstance(dj, Not) and dj.operand == di):
                rest_di = [d for d in disjuncts_ci if d != di]
                rest_dj = [d for d in disjuncts_cj if d != dj]
                combined = rest_di + rest_dj
                if not combined:
                    resolvents.append(False)
                else:
                    unique_literals = []
                    seen_formulas = set()
                    for lit in sorted(combined, key=lambda x: x.formula()):
                        formula = lit.formula()
                        if formula not in seen_formulas:
                            unique_literals.append(lit)
                            seen_formulas.add(formula)
                    if unique_literals and not is_tautology(Or(*unique_literals)):
                        resolvent = unique_literals[0] if len(unique_literals) == 1 else Or(*unique_literals)
                        resolvents.append(resolvent)
    return resolvents

def flatten_and_clauses(clauses):
    """Flatten And clauses into a list of CNF clauses."""
    result = []
    for clause in clauses:
        if isinstance(clause, And):
            result.extend(flatten_and_clauses(clause.conjuncts))
        else:
            result.append(to_cnf(clause))
    return result

def pl_resolution(kb, query, max_iterations=1000):
    """Implement resolution refutation with improved unit propagation."""
    clauses = flatten_and_clauses(kb.clauses.conjuncts)
    negate_query = to_cnf(Not(query))
    if isinstance(negate_query, And):
        clauses.extend(flatten_and_clauses(negate_query.conjuncts))
    else:
        clauses.append(negate_query)
    
    # Collect unit clauses
    unit_clauses = [c for c in clauses if isinstance(c, (Symbol, Not))]
    non_unit_clauses = [c for c in clauses if isinstance(c, Or)]
    
    # Simplify clauses with unit propagation
    simplified_clauses = []
    for clause in non_unit_clauses:
        simplified = simplify_clause(clause, unit_clauses)
        if simplified and not is_tautology(simplified):
            simplified_clauses.append(simplified)
        elif simplified is False:
            print(f"Contradiction found during simplification for query {query.formula()}")
            return True
    clauses = unit_clauses + simplified_clauses
    
    # Debug: Print initial clauses
    # print(f"Initial clauses for query {query.formula()}: {[c.formula() for c in clauses]}")
    
    new = set()
    iteration = 0
    while iteration < max_iterations:
        # print(f"\nIteration {iteration}: {len(clauses)} clauses")
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]
        
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                print(f"Contradiction found in resolution: {ci.formula()} and {cj.formula()}")
                return True
            for r in resolvents:
                if r and not is_tautology(r):
                    simplified = simplify_clause(r, unit_clauses)
                    if simplified is False:
                        print(f"Contradiction found in resolvent: {r.formula()}")
                        return True
                    if simplified and not is_tautology(simplified):
                        new.add(simplified)
        
        # Update unit clauses
        new_units = [c for c in new if isinstance(c, (Symbol, Not))]
        unit_clauses.extend(new_units)
        
        # Simplify all clauses with new units
        new_clauses = []
        for clause in clauses + list(new):
            simplified = simplify_clause(clause, unit_clauses)
            if simplified is False:
                print(f"Contradiction found in simplification: {clause.formula()}")
                return True
            if simplified and not is_tautology(simplified) and simplified not in new_clauses:
                new_clauses.append(simplified)
        clauses = new_clauses
        
        # Check for subsumption
        normalized_new = {normalize_clause(c) for c in new if c is not None}
        normalized_clauses = {normalize_clause(c) for c in clauses if c is not None}
        if not normalized_new or normalized_new.issubset(normalized_clauses):
            # print("No new non-subsumed clauses, terminating.")
            return False
        
        clauses.extend([c for c in new if normalize_clause(c) not in normalized_clauses])
        new.clear()
        iteration += 1
    
    print(f"Reached max iterations ({max_iterations}).")
    return False