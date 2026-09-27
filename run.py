import sys
import uvicorn
from backend.config import settings

# Force utf-8 stdout encoding for Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Hexo Elite AI - Autonomous Website Builder")
    print(f"Hindsight Memory Bank: {settings.hindsight_bank_id}")
    print(f"Dashboard URL: http://localhost:{settings.port}")
    print("=" * 60)
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
