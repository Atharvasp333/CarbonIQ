#!/usr/bin/env python3
"""
Installation Verification Script
Run this to verify all components are properly installed
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'boto3': 'AWS SDK (boto3)',
        'httpx': 'HTTPX',
        'pydantic': 'Pydantic',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} (Missing - run: pip install {module})")
            all_ok = False
    
    return all_ok


def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    
    required_files = [
        'backend/main.py',
        'backend/routes/aws_integration.py',
        'backend/services/s3_fetcher.py',
        'backend/services/aws_analyzer.py',
        'backend/models/schemas.py',
        'frontend/src/components/AWSIntegration.jsx',
        'frontend/src/api/client.js',
        'frontend/src/App.jsx',
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (Missing)")
            all_ok = False
    
    return all_ok


def check_backend_imports():
    """Check if backend modules can be imported"""
    print("\nChecking backend imports...")
    
    sys.path.insert(0, 'backend')
    
    modules = [
        ('routes.aws_integration', 'AWS Integration Route'),
        ('services.s3_fetcher', 'S3 Fetcher Service'),
        ('services.aws_analyzer', 'AWS Analyzer Service'),
    ]
    
    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name} (Error: {e})")
            all_ok = False
    
    return all_ok


def check_documentation():
    """Check if documentation files exist"""
    print("\nChecking documentation...")
    
    docs = [
        'AWS_INTEGRATION_README.md',
        'QUICK_START.md',
        'FEATURE_SUMMARY.md',
        'ARCHITECTURE_DIAGRAM.md',
    ]
    
    all_ok = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"✓ {doc}")
        else:
            print(f"✗ {doc} (Missing)")
            all_ok = False
    
    return all_ok


def main():
    """Run all checks"""
    print("=" * 60)
    print("AWS Integration - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Required Files", check_files),
        ("Backend Imports", check_backend_imports),
        ("Documentation", check_documentation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks PASSED! Installation is complete.")
        print("\nNext steps:")
        print("1. cd backend && uvicorn main:app --reload")
        print("2. cd frontend && npm run dev")
        print("3. Open http://localhost:5173")
        return 0
    else:
        print("❌ Some checks FAILED. Please fix the issues above.")
        print("\nCommon fixes:")
        print("• Install missing dependencies: pip install -r backend/requirements.txt")
        print("• Ensure you're in the project root directory")
        print("• Check that all files were created correctly")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
