"""
SkillSwap Main Entry Point
Runs both domains concurrently:
  - Youth/Senior on port 5000
  - Admin on port 5001
"""
import multiprocessing
from app import create_app, create_admin_app


import logging
import sys
import os

def run_main():
    """Run main app on port 5000"""
    # Simply run the app without suppression hacks to ensure stability
    app = create_app()
    app.run(debug=False, port=5000, threaded=True)

    
def run_admin():
    """Run admin app on port 5001"""
    # Simply run the app without suppression hacks to ensure stability
    app = create_admin_app()
    app.run(debug=False, port=5001, threaded=True)


if __name__ == "__main__":  
    print("=" * 55)
    print("SKILLSWAP - Starting Both Domains")
    print("=" * 55)
    print("  Youth/Senior: http://localhost:5000")
    print("  Admin:        http://localhost:5001")
    print("=" * 55)
    
    # Run both apps in separate processes
    main_process = multiprocessing.Process(target=run_main)
    admin_process = multiprocessing.Process(target=run_admin)
    
    main_process.start()
    admin_process.start()
    
    try:
        main_process.join()
        admin_process.join()
    except KeyboardInterrupt:
        pass
        # Terminate processes silently
        main_process.terminate()
        admin_process.terminate()