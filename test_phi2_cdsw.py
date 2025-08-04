#!/usr/bin/env python3
"""
Test script for CDSW Phi-2 model loading
Run this before deploying the full application
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_phi2_model():
    """Test Phi-2 GGUF model loading in CDSW environment"""
    
    print("🧪 CDSW Phi-2 Model Test")
    print("=" * 50)
    
    # Step 1: Check environment
    print("\n1️⃣ Checking CDSW Environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Current directory: {os.getcwd()}")
    
    # Step 2: Check model file
    print("\n2️⃣ Checking Model File...")
    model_paths = [
        "phi-2.Q4_K_M.gguf",
        "models/phi-2.Q4_K_M.gguf",
        "/home/cdsw/phi-2.Q4_K_M.gguf"
    ]
    
    model_found = False
    model_path = None
    
    for path in model_paths:
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024**3)  # GB
            print(f"   ✅ Found: {path} ({size:.2f} GB)")
            model_found = True
            model_path = path
            break
        else:
            print(f"   ❌ Not found: {path}")
    
    if not model_found:
        print("\n❌ CRITICAL: No Phi-2 GGUF model found!")
        print("   Please upload phi-2.Q4_K_M.gguf to your CDSW project root")
        return False
    
    # Step 3: Check dependencies
    print("\n3️⃣ Checking Dependencies...")
    
    try:
        import ctransformers
        print(f"   ✅ ctransformers: {ctransformers.__version__}")
    except ImportError:
        print("   ❌ ctransformers not installed")
        print("   Run: pip install ctransformers==0.2.27")
        return False
    
    try:
        import flask
        print(f"   ✅ flask: {flask.__version__}")
    except ImportError:
        print("   ❌ flask not installed")
        return False
    
    try:
        import yaml
        print("   ✅ pyyaml: available")
    except ImportError:
        print("   ❌ pyyaml not installed")
        return False
    
    # Step 4: Test model loading
    print("\n4️⃣ Testing Phi-2 Model Loading...")
    
    try:
        from ctransformers import AutoModelForCausalLM
        
        # Set CDSW environment
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        print("   🔄 Loading Phi-2 model (this may take 60-120 seconds)...")
        
        # Try different model types
        model_types = ["phi", "gpt2", "llama"]
        model_loaded = False
        
        for model_type in model_types:
            try:
                print(f"   🧠 Trying model_type: {model_type}")
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    model_type=model_type,
                    gpu_layers=0,  # CPU only
                    threads=4,
                    context_length=1024,  # Smaller for testing
                    mmap=True,
                    batch_size=1
                )
                
                # Test generation
                print("   🧪 Testing generation...")
                test_output = model("Hello", max_new_tokens=10)
                print(f"   📝 Test output: {test_output}")
                
                print(f"   ✅ Phi-2 model loaded successfully with type: {model_type}")
                model_loaded = True
                break
                
            except Exception as e:
                print(f"   ⚠️ Model type '{model_type}' failed: {str(e)[:100]}...")
                continue
        
        if not model_loaded:
            print("   ❌ All model types failed to load")
            return False
            
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Step 5: Memory check
    print("\n5️⃣ Checking Memory Usage...")
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   💾 Total memory: {memory.total / (1024**3):.1f} GB")
        print(f"   💾 Available memory: {memory.available / (1024**3):.1f} GB")
        print(f"   💾 Used memory: {memory.used / (1024**3):.1f} GB")
        
        if memory.available < 10 * (1024**3):  # Less than 10GB available
            print("   ⚠️ Warning: Low available memory for CDSW deployment")
        else:
            print("   ✅ Sufficient memory for CDSW deployment")
            
    except ImportError:
        print("   ℹ️ psutil not available for memory check")
    
    print("\n🎉 SUCCESS: Phi-2 model test completed!")
    print("   Your CDSW environment is ready for Phi-2 UAT Generator")
    return True

def main():
    """Main test function"""
    success = test_phi2_model()
    
    if success:
        print("\n" + "="*50)
        print("✅ CDSW PHI-2 TEST PASSED")
        print("="*50)
        print("Next steps:")
        print("1. Run: python app_cdsw_phi2_only.py")
        print("2. Access your CDSW application URL")
        print("3. Test UAT generation with a user story")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ CDSW PHI-2 TEST FAILED")
        print("="*50)
        print("Please fix the issues above before deploying")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
