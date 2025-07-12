#!/usr/bin/env python3
"""
Simple test script to verify bot setup
"""

import sqlite3
import sys

def test_database():
    """Test database connection and content"""
    try:
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Database tables found: {[table[0] for table in tables]}")
        
        # Check words count
        cursor.execute("SELECT COUNT(*) FROM words")
        word_count = cursor.fetchone()[0]
        print(f"✅ Words in database: {word_count}")
        
        # Check sample words
        cursor.execute("SELECT term, definition FROM words LIMIT 3")
        sample_words = cursor.fetchall()
        print("\n📖 Sample words:")
        for term, definition in sample_words:
            print(f"  • {term}: {definition[:100]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import asyncio
        import logging
        import sqlite3
        import re
        from aiogram import Bot, Dispatcher, types
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
        from aiogram.filters import Command
        from aiogram.client.default import DefaultBotProperties
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from datetime import datetime
        from database import register_user, update_user_time
        
        print("✅ All required modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Academy Bot Setup\n")
    
    # Test imports
    print("1. Testing imports...")
    imports_ok = test_imports()
    
    # Test database
    print("\n2. Testing database...")
    db_ok = test_database()
    
    # Summary
    print("\n" + "="*50)
    if imports_ok and db_ok:
        print("✅ All tests passed! Bot is ready to run.")
        print("Run: python bot.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 