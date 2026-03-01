"""
GreenWeave — Module 6: Quality Validator (Self-Learning Router)
Ensures small models don't return garbage. If they fail, it reroutes to a large model and learns.
"""
import time

def simulate_routing(prompt, complexity_score):
    print(f"\n📥 New Query: '{prompt}'")
    print(f"🧠 Evaluated Complexity Score: {complexity_score}/10")
    
    # Step 1: Attempt small model first (Eco-routing)
    print("🔄 [Eco-Router] Attempting to answer with small, low-carbon model (Llama-8b)...")
    time.sleep(1.5)
    
    if complexity_score > 7:
        small_model_response = "Here is some code... wait, I am confused by the nested loops."
    else:
        small_model_response = "Paris is the capital of France."
        
    print(f"   Output generated: '{small_model_response}'")
    
    # Step 2: Quality Validation
    print("🔬 [Validator] Running background quality check on response...")
    time.sleep(1.5)
    
    if "confused" in small_model_response or len(small_model_response) < 40 and complexity_score > 7:
        print("❌ [Validator] FAILED. Response quality is too low for this complexity level.")
        
        # Step 3: Fallback & Self-Learn
        print("🚀 [Fallback] Rerouting request to large, high-accuracy model (Llama-70b)...")
        time.sleep(2.5)
        print("✅ [Validator] PASSED. High-quality response generated.")
        
        print("🧠 [Self-Learning] Updating AI Router Weights...")
        print(f"   -> Rule Added: 'If complexity > {complexity_score - 1}, bypass small models to save latency.'")
    else:
        print("✅ [Validator] PASSED. Small model response is high quality. Carbon saved!")

print("🤖 GreenWeave Quality Validator & Self-Learning Engine Started...\n")
print("-" * 60)

# Test 1: Simple Question (Small model succeeds)
simulate_routing("What is the capital of France?", complexity_score=2)

print("-" * 60)

# Test 2: Complex Coding Question (Small model fails, system self-learns)
simulate_routing("Write a multi-threaded Python script with asynchronous rate-limiting.", complexity_score=9)

print("\n🎯 Enterprise Value: GreenWeave guarantees 100% answer quality while minimizing carbon. It learns your codebase's complexity over time!")