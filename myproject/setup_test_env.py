import os
from pathlib import Path

def setup_test_environment():
    """Set up test environment variables"""
    # Path to the test .env file
    env_path = Path('myproject') / '.env.test'
    
    # Create test environment file
    test_env_content = """# Test Environment Configuration
TEST_MODE=true
RUN_ON_START=true
SKIP_POST=true
PYTHONUNBUFFERED=1
PYTHONIOENCODING=utf-8
"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(test_env_content)
    
    print(f"✅ Created test environment file at: {env_path}")
    print("Test configuration:")
    print(test_env_content)

if __name__ == "__main__":
    setup_test_environment()
