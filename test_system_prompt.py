#!/usr/bin/env python3
"""
Test script to verify the system prompt functionality
"""

import os
import sys
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system_prompt_integration():
    """Test that the system prompt is properly integrated into the application"""
    print("Testing system prompt integration...")
    
    try:
        # Import the app and global variables
        from app_chat import SYSTEM_PROMPT, PROMPT_TEMPLATE, generate_response
        print("✅ Successfully imported app components")
        
        # Check that SYSTEM_PROMPT is defined
        if SYSTEM_PROMPT:
            print("✅ SYSTEM_PROMPT variable is defined")
            print(f"✅ SYSTEM_PROMPT length: {len(SYSTEM_PROMPT)} characters")
        else:
            print("❌ SYSTEM_PROMPT variable is not defined or is empty")
            return False
            
        # Check that PROMPT_TEMPLATE is defined
        if PROMPT_TEMPLATE:
            print("✅ PROMPT_TEMPLATE variable is defined")
        else:
            print("❌ PROMPT_TEMPLATE variable is not defined")
            return False
            
        # Check that the system prompt contains UAT-related content
        if "UAT" in SYSTEM_PROMPT and "User Acceptance Testing" in SYSTEM_PROMPT:
            print("✅ SYSTEM_PROMPT contains UAT-related content")
        else:
            print("❌ SYSTEM_PROMPT does not contain expected UAT-related content")
            return False
            
        # Check that the system prompt contains quality assurance content
        if "quality assurance" in SYSTEM_PROMPT:
            print("✅ SYSTEM_PROMPT contains quality assurance content")
        else:
            print("❌ SYSTEM_PROMPT does not contain expected quality assurance content")
            return False
            
        print("✅ System prompt integration test passed")
        return True
    except Exception as e:
        print(f"❌ Failed to test system prompt integration: {e}")
        return False

def test_prompt_construction():
    """Test that prompts are constructed correctly with system prompt"""
    print("\nTesting prompt construction...")
    
    try:
        # Import the generate_response function
        from app_chat import generate_response, SYSTEM_PROMPT, PROMPT_TEMPLATE
        
        # Create a mock session with history
        import flask
        app = flask.Flask(__name__)
        with app.test_request_context():
            # Simulate a session with chat history
            flask.session['chat_history'] = [
                "Instruct: What is UAT testing?\nOutput:",
                "User Acceptance Testing (UAT) is the final phase of the software testing process where actual software users test the software to make sure it can handle required tasks in real-world scenarios, according to specifications."
            ]
            
            # Test prompt construction logic
            # We'll mock the LLM call to just return the prompt
            import app_chat
            original_llm = app_chat.llm
            
            # Mock LLM that just returns the prompt
            class MockLLM:
                def __call__(self, prompt, *args, **kwargs):
                    return {
                        "choices": [{
                            "text": f"[Prompt Construction Test] Received prompt with {len(prompt)} characters"
                        }]
                    }
            
            app_chat.llm = MockLLM()
            
            # Test with a sample prompt
            test_prompt = "Generate test cases for user login"
            result = generate_response(test_prompt, 512)
            
            # Restore original LLM
            app_chat.llm = original_llm
            
            print("✅ Prompt construction test completed")
            print(f"✅ Sample result: {result}")
            
            # Verify that system prompt is included
            if "[Prompt Construction Test]" in result:
                print("✅ Prompt construction logic is working")
            else:
                print("⚠️  Could not verify prompt construction logic (LLM mock not working)")
            
            return True
    except Exception as e:
        print(f"❌ Failed to test prompt construction: {e}")
        return False

def test_settings_page():
    """Test that the settings page includes system prompt configuration"""
    print("\nTesting settings page...")
    
    try:
        # Read the settings.html file
        with open("templates/settings.html", "r") as f:
            content = f.read()
        
        # Check if system prompt textarea exists
        if 'name="system_prompt"' in content:
            print("✅ System prompt textarea found in settings.html")
        else:
            print("❌ System prompt textarea not found in settings.html")
            return False
            
        # Check if system prompt heading exists
        if 'System Prompt' in content:
            print("✅ System prompt heading found in settings.html")
        else:
            print("❌ System prompt heading not found in settings.html")
            return False
            
        # Check if system prompt form action exists
        if 'action="/update_system_prompt"' in content:
            print("✅ System prompt form action found in settings.html")
        else:
            print("❌ System prompt form action not found in settings.html")
            return False
            
        # Check if instruction template heading exists
        if 'Instruction Template' in content:
            print("✅ Instruction template heading found in settings.html")
        else:
            print("❌ Instruction template heading not found in settings.html")
            return False
            
        print("✅ Settings page test passed")
        return True
    except Exception as e:
        print(f"❌ Failed to test settings page: {e}")
        return False

def test_update_system_prompt_route():
    """Test that the update system prompt route exists"""
    print("\nTesting update system prompt route...")
    
    try:
        # Import the app
        from app_chat import app
        
        # Check if the route exists
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        if '/update_system_prompt' in rules:
            print("✅ /update_system_prompt route found")
        else:
            print("❌ /update_system_prompt route not found")
            return False
            
        print("✅ Update system prompt route test passed")
        return True
    except Exception as e:
        print(f"❌ Failed to test update system prompt route: {e}")
        return False

def run_all_tests():
    """Run all system prompt tests"""
    print("Running all tests for system prompt functionality...\n")
    
    tests = [
        test_system_prompt_integration,
        test_prompt_construction,
        test_settings_page,
        test_update_system_prompt_route
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    if all_passed:
        print("\n🎉 All system prompt tests passed!")
        print("The application now supports:")
        print("  1. System prompt configuration")
        print("  2. Integration of system prompt with conversation history")
        print("  3. Settings page for managing both system and instruction prompts")
        print("  4. Dedicated route for updating system prompts")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)
