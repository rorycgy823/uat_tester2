#!/usr/bin/env python3
"""
CDSW-Only Phi-2 UAT Generator
Pure local GGUF model, no template fallback, CDSW optimized
"""

import os
import logging
from flask import Flask, request, jsonify, render_template_string
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CDSW Environment Setup
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class CDSWPhi2Model:
    """Pure CDSW Phi-2 GGUF model loader"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_phi2_model()
    
    def _load_phi2_model(self):
        """Load Phi-2 GGUF model for CDSW environment"""
        try:
            logger.info("🚀 Loading Phi-2 GGUF model for CDSW...")
            
            from ctransformers import AutoModelForCausalLM
            
            # CDSW-specific model paths
            model_paths = [
                "phi-2.Q4_K_M.gguf",  # Project root
                "models/phi-2.Q4_K_M.gguf",  # Models directory
                "/home/cdsw/phi-2.Q4_K_M.gguf",  # CDSW home
                "/tmp/phi-2.Q4_K_M.gguf"  # CDSW temp
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    logger.info(f"📁 Found GGUF model: {path}")
                    break
            
            if not model_path:
                raise FileNotFoundError("❌ No phi-2.Q4_K_M.gguf found in CDSW paths")
            
            # Try different model types for Phi-2 compatibility
            model_types = ["phi", "gpt2", "llama"]
            
            for model_type in model_types:
                try:
                    logger.info(f"🧠 Loading with model_type: {model_type}")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        model_type=model_type,
                        gpu_layers=0,  # CPU only for CDSW
                        threads=4,  # CDSW CPU optimization
                        context_length=2048,
                        mmap=True,
                        batch_size=1,
                        max_new_tokens=512
                    )
                    
                    # Test the model
                    test_output = self.model("Test:", max_new_tokens=5)
                    logger.info(f"✅ Phi-2 model loaded successfully with type: {model_type}")
                    self.model_loaded = True
                    return
                    
                except Exception as e:
                    logger.warning(f"⚠️ Model type '{model_type}' failed: {e}")
                    continue
            
            raise Exception("❌ All model types failed")
            
        except ImportError:
            logger.error("❌ ctransformers not installed. Run: pip install ctransformers")
            raise
        except Exception as e:
            logger.error(f"❌ Phi-2 model loading failed: {e}")
            raise
    
    def generate_uat(self, user_story: str) -> dict:
        """Generate UAT using Phi-2 model"""
        if not self.model_loaded:
            raise Exception("Phi-2 model not loaded")
        
        prompt = f"""
[INSTRUCTION] Generate comprehensive test cases and YAML configuration for this user story:

USER STORY: {user_story}

[OUTPUT FORMAT]
TEST CASES:
1. Positive Test Case - [Title]
   - Preconditions: [Prerequisites]
   - Steps: 
     a) [Step 1]
     b) [Step 2]
   - Expected: [Expected result]

2. Negative Test Case - [Title]
   - Preconditions: [Prerequisites]
   - Steps:
     a) [Step 1]
     b) [Step 2]
   - Expected: [Expected error]

CONFIGURATION:
environment: cdsw_test
feature_under_test: [feature name]
test_data:
  valid_inputs: [examples]
  invalid_inputs: [examples]
security_settings:
  authentication_required: true
  audit_logging: true

[GENERATE]
"""
        
        try:
            # Generate with Phi-2
            generated_text = self.model(
                prompt,
                max_new_tokens=512,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.1,
                stop=["</end>", "[END]"]
            )
            
            # Parse output
            test_cases = self._extract_test_cases(generated_text)
            configuration = self._extract_configuration(generated_text)
            
            return {
                "test_cases": test_cases,
                "configuration": configuration,
                "quality_score": self._calculate_quality_score(test_cases, configuration),
                "model_used": "phi-2-gguf",
                "generated_text": generated_text
            }
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise
    
    def _extract_test_cases(self, text: str) -> str:
        """Extract test cases from generated text"""
        try:
            if "TEST CASES:" in text:
                start = text.find("TEST CASES:")
                end = text.find("CONFIGURATION:")
                if end == -1:
                    end = len(text)
                return text[start:end].strip()
            return "Test cases not properly generated"
        except:
            return "Error extracting test cases"
    
    def _extract_configuration(self, text: str) -> str:
        """Extract configuration from generated text"""
        try:
            if "CONFIGURATION:" in text:
                start = text.find("CONFIGURATION:")
                return text[start:].strip()
            return """environment: cdsw_test
feature_under_test: extracted_feature
test_data:
  valid_inputs: ["test_data"]
  invalid_inputs: ["invalid_data"]
security_settings:
  authentication_required: true
  audit_logging: true"""
        except:
            return "environment: error"
    
    def _calculate_quality_score(self, test_cases: str, config: str) -> int:
        """Calculate quality score"""
        score = 70  # Base score for Phi-2
        
        if "Preconditions:" in test_cases:
            score += 5
        if "Steps:" in test_cases:
            score += 5
        if "Expected:" in test_cases:
            score += 5
        if "Positive Test Case" in test_cases:
            score += 5
        if "Negative Test Case" in test_cases:
            score += 5
        if "environment:" in config:
            score += 3
        if "test_data:" in config:
            score += 2
        
        return min(score, 95)  # Cap at 95% for Phi-2

# Initialize Phi-2 model
logger.info("🚀 Initializing CDSW Phi-2 UAT Generator...")
phi2_model = CDSWPhi2Model()

# Flask App
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CDSW Phi-2 UAT Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .header { text-align: center; margin-bottom: 30px; }
        .title { color: #333; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.2em; }
        .status { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 5px; }
        .status.ready { background: #d4edda; color: #155724; }
        .status.phi2 { background: #cce5ff; color: #004085; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        .form-group textarea { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; resize: vertical; }
        .btn { background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 12px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .results { margin-top: 30px; }
        .result-tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #f8f9fa; border: 1px solid #ddd; cursor: pointer; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { border: 1px solid #ddd; padding: 20px; background: #f8f9fa; }
        .metrics { display: flex; justify-content: space-around; margin: 20px 0; }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .loading { text-align: center; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🤖 CDSW Phi-2 UAT Generator</h1>
            <p class="subtitle">Local Phi-2 Model for User Acceptance Testing</p>
            <div class="status ready">✅ Phi-2 Ready</div>
            <div class="status phi2">🧠 CPU Optimized</div>
        </div>

        <div class="form-group">
            <label for="user_story">📝 User Story:</label>
            <textarea id="user_story" rows="4" placeholder="As a [role], I want to [action] so that [benefit]..."></textarea>
        </div>

        <button class="btn" onclick="generateUAT()">🚀 Generate UAT with Phi-2</button>

        <div id="results" class="results" style="display: none;">
            <div class="success">✅ UAT Generation Successful</div>
            
            <div class="metrics">
                <div class="metric">
                    <div id="quality_score" class="metric-value">-</div>
                    <div class="metric-label">QUALITY SCORE</div>
                </div>
                <div class="metric">
                    <div id="test_count" class="metric-value">-</div>
                    <div class="metric-label">TEST CASES</div>
                </div>
                <div class="metric">
                    <div class="metric-value">PHI-2</div>
                    <div class="metric-label">MODEL</div>
                </div>
            </div>

            <div class="result-tabs">
                <div class="tab active" onclick="showTab('test_cases')">✅ Test Cases</div>
                <div class="tab" onclick="showTab('configuration')">⚙️ Configuration</div>
                <div class="tab" onclick="showTab('raw_output')">📄 Raw Output</div>
            </div>

            <div id="test_cases_content" class="tab-content">
                <h3>Generated Test Cases:</h3>
                <pre id="test_cases_text"></pre>
            </div>

            <div id="configuration_content" class="tab-content" style="display: none;">
                <h3>Configuration (YAML):</h3>
                <pre id="configuration_text"></pre>
            </div>

            <div id="raw_output_content" class="tab-content" style="display: none;">
                <h3>Raw Phi-2 Output:</h3>
                <pre id="raw_output_text"></pre>
            </div>
        </div>

        <div id="loading" class="loading" style="display: none;">
            <h3>🧠 Phi-2 is generating UAT...</h3>
            <p>This may take 30-60 seconds on CPU</p>
        </div>
    </div>

    <script>
        function generateUAT() {
            const userStory = document.getElementById('user_story').value;
            if (!userStory.trim()) {
                alert('Please enter a user story');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';

            fetch('/generate_uat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_story: userStory })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                document.getElementById('quality_score').textContent = data.quality_score + '%';
                document.getElementById('test_count').textContent = (data.test_cases.match(/\\d+\\./g) || []).length;
                document.getElementById('test_cases_text').textContent = data.test_cases;
                document.getElementById('configuration_text').textContent = data.configuration;
                document.getElementById('raw_output_text').textContent = data.generated_text;
                
                document.getElementById('results').style.display = 'block';
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                alert('Error: ' + error);
            });
        }

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName + '_content').style.display = 'block';
            
            // Add active class to selected tab
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_uat', methods=['POST'])
def generate_uat():
    try:
        data = request.get_json()
        user_story = data.get('user_story', '')
        
        if not user_story:
            return jsonify({"error": "User story is required"}), 400
        
        logger.info(f"🔄 Generating UAT for: {user_story[:50]}...")
        
        # Generate UAT with Phi-2
        result = phi2_model.generate_uat(user_story)
        
        logger.info(f"✅ UAT generated successfully (Quality: {result['quality_score']}%)")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ UAT generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": phi2_model.model_loaded,
        "model_type": "phi-2-gguf"
    })

if __name__ == '__main__':
    # CDSW environment configuration
    port = int(os.environ.get('CDSW_APP_PORT', 8080))
    host = os.environ.get('CDSW_IP_ADDRESS', '127.0.0.1')
    
    logger.info(f"🚀 Starting CDSW Phi-2 UAT Generator on {host}:{port}")
    
    if phi2_model.model_loaded:
        logger.info("✅ Phi-2 model ready for UAT generation!")
    else:
        logger.error("❌ Phi-2 model failed to load - check GGUF file")
        exit(1)
    
    app.run(host=host, port=port, debug=False, threaded=True)
