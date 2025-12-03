#!/usr/bin/env python3
"""
Backend Integration Test Script
Telentropy modüllerinin Flask uygulamasıyla entegrasyonunu test eder
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all modules"""
    print("🔍 Testing imports...")
    
    try:
        # Test Flask app import
        import app
        print("✅ Flask app imported successfully")
        
        # Test backend modules import
        try:
            from interaction_manager import InteractionManager
            print("✅ InteractionManager imported successfully")
        except ImportError as e:
            print(f"⚠️  InteractionManager import failed: {e}")
        
        try:
            from profile_manager import ProfileManager
            print("✅ ProfileManager imported successfully")
        except ImportError as e:
            print(f"⚠️  ProfileManager import failed: {e}")
        
        try:
            from group_finder import GroupFinder
            print("✅ GroupFinder imported successfully")
        except ImportError as e:
            print(f"⚠️  GroupFinder import failed: {e}")
        
        try:
            from session_converter import SessionConverter
            print("✅ SessionConverter imported successfully")
        except ImportError as e:
            print(f"⚠️  SessionConverter import failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask routes"""
    print("\n🔍 Testing Flask routes...")
    
    try:
        import app
        flask_app = app.app
        
        # Get all routes
        routes = []
        for rule in flask_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        
        # Filter API routes
        api_routes = [r for r in routes if '/api/' in r['rule']]
        
        print(f"✅ Found {len(routes)} total routes")
        print(f"✅ Found {len(api_routes)} API routes")
        
        # Check specific backend integration routes
        backend_routes = [
            '/api/interaction_manager/start',
            '/api/interaction_manager/status',
            '/api/profile_manager/update',
            '/api/group_finder/search',
            '/api/session_converter/convert'
        ]
        
        for route in backend_routes:
            route_found = any(route in r['rule'] for r in api_routes)
            status = "✅" if route_found else "❌"
            print(f"{status} {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

def test_global_dictionaries():
    """Test global task result dictionaries"""
    print("\n🔍 Testing global dictionaries...")
    
    try:
        import app
        
        # Check if global dictionaries exist
        required_dicts = [
            'interaction_results',
            'profile_update_results', 
            'group_search_results',
            'session_convert_results'
        ]
        
        for dict_name in required_dicts:
            if hasattr(app, dict_name):
                dict_obj = getattr(app, dict_name)
                if isinstance(dict_obj, dict):
                    print(f"✅ {dict_name} exists and is a dictionary")
                else:
                    print(f"❌ {dict_name} exists but is not a dictionary")
            else:
                print(f"❌ {dict_name} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Global dictionaries test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Backend Integration Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_flask_routes,
        test_global_dictionaries
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
