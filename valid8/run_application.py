#!/usr/bin/env python3
"""
Certificate Verification System - Database Version
Main application entry point (No Blockchain - Uses Regular Database)

Run with: python run_application.py
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main_app import create_app

def main():
    """Main function to run the application"""

    # Create Flask application
    app = create_app()

    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"""
    🚀 Certificate Verification System Starting...

    📊 Environment: Development (Database Version - No Blockchain)
    🌐 URL: http://{host}:{port}
    🔧 Debug Mode: {debug}

    🏠 Pages Available:
    ├── Certificate Verification: http://{host}:{port}/
    ├── Institution Login: http://{host}:{port}/auth/institution/login
    ├── Institution Signup: http://{host}:{port}/auth/institution/signup
    └── Admin Dashboard: http://{host}:{port}/admin/login

    📝 Demo Credentials:
    ├── Admin: admin / admin123
    ├── Institution: tech_univ_001 / password123
    ├── Valid Institution Codes: TECH_UNIV_001, BIZ_COLLEGE_002, MED_SCHOOL_003

    🔍 Features:
    ├── ✅ 8-Step Certificate Verification Process
    ├── ✅ AI-Powered OCR Text Extraction  
    ├── ✅ Watermark Detection using Computer Vision
    ├── ✅ Digital Signature Verification
    ├── ✅ Database Storage with Hash Generation
    ├── ✅ Mock API Calls to External Services
    ├── ✅ Institution Authentication & Management
    ├── ✅ Admin Dashboard with Flag Management
    ├── ✅ Single & Bulk Certificate Upload
    └── ✅ Real-time Search & Verification

    Press Ctrl+C to stop the server
    """)

    try:
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Certificate Verification System stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
