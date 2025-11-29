import sys
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

try:
    import fpdf
    print(f"fpdf imported from: {fpdf.__file__}")
    print(f"fpdf dir: {dir(fpdf)}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
