from knowledgeBase import KnowledgeBase
from object import Stench, Breeze
from logic import Symbol, Not

def test_percept_handling():
    # Initialize KB with a 4x4 grid for simplicity
    kb = KnowledgeBase(N=4)
    
    # Test case 1: Adding Stench percept
    pos = (2, 2)  # Testing at position (2,2)
    percepts = [Stench()]
    
    print("Test Case 1: Adding Stench percept at (2,2)")
    print("Initial clause formulas:", kb.clause_formulas)
    
    # First, let's add a negation of Stench to simulate existing knowledge
    stench_symbol = kb.symbols[('Stench', 2, 2)]
    kb += Not(stench_symbol)
    print("After adding Not(Stench):", kb.clause_formulas)
    
    # Now update with actual Stench percept
    kb.update_percept_sentence(pos, percepts)
    print("After updating with Stench percept:", kb.clause_formulas)
    print(f"Stench symbol at (2,2) present:", stench_symbol.formula() in str(kb.clauses))
    
    # Test case 2: Adding Breeze percept without prior negative knowledge
    pos = (3, 3)
    percepts = [Breeze()]
    
    print("\nTest Case 2: Adding Breeze percept at (3,3)")
    print("Initial state for Breeze:", kb.clause_formulas)
    kb.update_percept_sentence(pos, percepts)
    breeze_symbol = kb.symbols[('Breeze', 3, 3)]
    print("After adding Breeze:", kb.clause_formulas)
    print(f"Breeze symbol at (3,3) present:", breeze_symbol.formula() in str(kb.clauses))

if __name__ == "__main__":
    test_percept_handling()
