"""Setup verification script."""
import sys
from app.config import get_settings

def test_setup():
    """Verify environment and dependencies."""
    print("🔍 Checking Python version...")
    print(f"   Python {sys.version}")
    
    print("\n🔍 Loading configuration...")
    settings = get_settings()
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug Mode: {settings.debug}")
    print(f"   Default Location: {settings.default_location_name}")
    print(f"   Coordinates: ({settings.default_location_lat}, {settings.default_location_lon})")
    
    print("\n🔍 Checking dependencies...")
    try:
        import fastapi
        import pydantic
        import httpx
        print("   ✅ FastAPI installed")
        print("   ✅ Pydantic installed")
        print("   ✅ HTTPX installed")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False
    
    print("\n✅ Setup verification complete! Ready to build.")
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)