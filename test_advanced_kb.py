#!/usr/bin/env python3
"""
Test file for Advanced Mode Knowledge Base
Tests the functionality of KnowledgeBase when is_advanced=True
"""

from knowledgeBase import KnowledgeBase, build_init_kb
from environment import WumpusEnvironment
from object import Stench, Breeze, Glitter, Bump, Scream
from logic import Not
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_basic_kb_creation():
    """Test basic KB creation in advanced mode"""
    print("=" * 50)
    print("TEST 1: Basic KB Creation (Advanced Mode)")
    print("=" * 50)
    
    kb = KnowledgeBase(N=4, is_advanced=True)
    
    print(f"KB Width: {kb.width}")
    print(f"KB Height: {kb.height}")
    print(f"Is Advanced: {kb.is_advanced}")
    print(f"Action Count: {kb.action_count}")
    print(f"Visited positions: {kb.visited}")
    print(f"Number of initial clauses: {len(kb.clause_formulas)}")
    print(f"Initial clauses: {kb.clause_formulas}")

    # Test some basic symbol access
    print(f"Wumpus_1_1 symbol: {kb.symbols[('Wumpus', 1, 1)]}")
    print(f"Stench_2_2 symbol: {kb.symbols[('Stench', 2, 2)]}")
    
    print("✓ Basic KB creation test passed\n")

def test_advanced_mode_clause_removal():
    """Test clause removal in advanced mode every 5 actions"""
    print("=" * 50)
    print("TEST 2: Advanced Mode Clause Removal")
    print("=" * 50)
    
    kb = KnowledgeBase(N=4, is_advanced=True)
    
    # Add some stench percepts
    kb.update_percept_sentence((2, 2), [Stench()])
    kb.update_percept_sentence((2, 3), [Stench()])
    
    print(f"Initial clauses count: {len(kb.clause_formulas)}")
    print(f"Initial visited: {kb.visited}")
    
    # Simulate actions to trigger clause removal (every 5 actions)
    class MockAgent:
        def __init__(self):
            self.location = (1, 1)
            self.direction = MockDirection()
    
    class MockDirection:
        def __init__(self):
            self.direction = 'up'
    
    agent = MockAgent()
    
    # Perform 5 actions to trigger clause removal
    for i in range(5):
        kb.update_action_sentence(agent, 'Move', i)
        print(f"Action {i+1}: Action count = {kb.action_count}")
    
    print(f"After 5 actions - clauses count: {len(kb.clause_formulas)}")
    print(f"After 5 actions - visited: {kb.visited}")
    
    print("✓ Advanced mode clause removal test completed\n")

def test_stench_handling_advanced_mode():
    """Test stench handling in advanced mode"""
    print("=" * 50)
    print("TEST 3: Stench Handling in Advanced Mode")
    print("=" * 50)
    
    kb = KnowledgeBase(N=4, is_advanced=True)
    
    # Test adding stench percept
    print("Adding stench at (2, 2)...")
    kb.update_percept_sentence((2, 2), [Stench()])
    
    stench_symbol = kb.symbols[('Stench', 2, 2)]
    stench_formula = stench_symbol.formula()
    
    print(f"Stench formula: {stench_formula}")
    print(f"Is stench formula in clauses: {stench_formula in kb.clause_formulas}")
    
    # Test removing stench (what happens when no stench is detected)
    print("Updating (2, 2) with no stench...")
    kb.update_percept_sentence((2, 2), [])
    
    print(f"After no stench - is stench formula in clauses: {stench_formula in kb.clause_formulas}")
    
    # Test re-adding stench after removal
    print("Re-adding stench at (2, 2)...")
    kb.update_percept_sentence((2, 2), [Stench()])
    
    print(f"After re-adding - is stench formula in clauses: {stench_formula in kb.clause_formulas}")
    
    print("✓ Stench handling test completed\n")

def test_wumpus_knowledge_advanced_mode():
    """Test Wumpus knowledge handling in advanced mode"""
    print("=" * 50)
    print("TEST 4: Wumpus Knowledge in Advanced Mode")
    print("=" * 50)
    
    kb = KnowledgeBase(N=4, is_advanced=True)
    
    # Test querying Wumpus knowledge
    wumpus_1_1 = kb.symbols[('Wumpus', 1, 1)]
    wumpus_2_2 = kb.symbols[('Wumpus', 2, 2)]
    
    print("Testing Wumpus knowledge queries...")
    
    # Query if there's no Wumpus at (1,1) - should be True due to initial knowledge
    no_wumpus_1_1 = kb.ask(Not(wumpus_1_1))
    print(f"No Wumpus at (1,1): {no_wumpus_1_1}")
    
    # Add knowledge that we visited (2,2) - should add no Wumpus there
    kb.update_percept_sentence((2, 2), [])
    no_wumpus_2_2 = kb.ask(Not(wumpus_2_2))
    print(f"No Wumpus at (2,2) after visiting: {no_wumpus_2_2}")
    
    print("✓ Wumpus knowledge test completed\n")

def test_environment_integration():
    """Test KB integration with environment in advanced mode"""
    print("=" * 50)
    print("TEST 5: Environment Integration (Advanced Mode)")
    print("=" * 50)
    
    # Create environment with advanced setting
    env = WumpusEnvironment(N=4, K_wumpuses=1, pit_probability=0.1, advanced_setting=True)
    
    print(f"Environment advanced setting: {env.is_advanced}")
    print(f"Wumpus positions: {env.wumpus_pos}")
    print(f"Pit positions: {env.pit_pos}")
    
    # Build KB with advanced mode
    kb = build_init_kb(4, env, is_advanced=True)
    
    print(f"KB advanced mode: {kb.is_advanced}")
    print(f"KB initial visited: {kb.visited}")
    
    # Get initial percepts
    initial_percepts = env.percept((1, 1))
    print(f"Initial percepts at (1,1): {[type(p).__name__ for p in initial_percepts]}")
    
    print("✓ Environment integration test completed\n")

def test_action_counting_and_reset():
    """Test action counting and periodic reset in advanced mode"""
    print("=" * 50)
    print("TEST 6: Action Counting and Reset")
    print("=" * 50)
    
    kb = KnowledgeBase(N=4, is_advanced=True)
    
    # Add some knowledge
    kb.update_percept_sentence((2, 1), [Stench()])
    kb.update_percept_sentence((1, 2), [Breeze()])
    kb.update_percept_sentence((3, 3), [])
    
    print(f"Initial state:")
    print(f"  Action count: {kb.action_count}")
    print(f"  Visited: {kb.visited}")
    print(f"  Clause count: {len(kb.clause_formulas)}")
    
    class MockAgent:
        def __init__(self):
            self.location = (1, 1)
            self.direction = MockDirection()
    
    class MockDirection:
        def __init__(self):
            self.direction = 'up'
    
    agent = MockAgent()
    
    # Perform exactly 5 actions to trigger reset
    for i in range(6):
        kb.update_action_sentence(agent, 'Move', i)
        print(f"  After action {i+1}: Action count = {kb.action_count}")
        
        if (i + 1) % 5 == 0:
            print(f"  *** RESET TRIGGERED at action {i+1} ***")
            print(f"  Visited after reset: {kb.visited}")
            print(f"  Clause count after reset: {len(kb.clause_formulas)}")
    
    print("✓ Action counting and reset test completed\n")

def run_all_tests():
    """Run all advanced mode KB tests"""
    print("🚀 STARTING ADVANCED MODE KNOWLEDGE BASE TESTS")
    print("=" * 60)
    
    try:
        test_basic_kb_creation()
        test_advanced_mode_clause_removal()
        test_stench_handling_advanced_mode()
        test_wumpus_knowledge_advanced_mode()
        test_environment_integration()
        test_action_counting_and_reset()
        
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
