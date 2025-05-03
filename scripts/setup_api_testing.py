#!/usr/bin/env python
"""
API Testing Setup Script

This script helps you set up your API testing approach, offering options to:
1. Keep the original e2e_api_test.py script (for quick manual testing)
2. Replace it with pytest-based API tests (more maintainable, supports CI)
3. Keep both approaches

The script doesn't delete any files; it can create symlinks or provide instructions.
"""

import os
import sys
import shutil
from pathlib import Path


def check_files():
    """Check if both test files exist."""
    e2e_api_test_exists = os.path.exists("e2e_api_test.py")
    pytest_api_test_exists = os.path.exists("tests/test_api_e2e.py")
    return e2e_api_test_exists, pytest_api_test_exists


def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def main():
    """Main function."""
    print("=" * 80)
    print("API Testing Setup")
    print("=" * 80)
    print("\nThis script helps you set up your API testing approach.")

    # Check if files exist
    e2e_api_test_exists, pytest_api_test_exists = check_files()

    if not e2e_api_test_exists and not pytest_api_test_exists:
        print("\nError: Neither e2e_api_test.py nor tests/test_api_e2e.py found.")
        print("Please ensure you're running this script from the project root directory.")
        return

    # Present options
    print("\nAvailable options:")
    print("1. Keep original e2e_api_test.py (for quick manual testing)")
    print("2. Use pytest-based API tests (more maintainable, supports CI)")
    print("3. Keep both approaches")
    print("4. Exit without making changes")

    try:
        choice = int(input("\nEnter your choice (1-4): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    if choice == 1:
        # Keep original e2e_api_test.py
        if not e2e_api_test_exists:
            print("\nError: e2e_api_test.py does not exist.")
            return
        print("\nKeeping original e2e_api_test.py")
        print("You can run manual API tests with: python e2e_api_test.py")

    elif choice == 2:
        # Use pytest-based API tests
        if not pytest_api_test_exists:
            print("\nError: tests/test_api_e2e.py does not exist.")
            return

        # Ask if user wants to backup or remove e2e_api_test.py
        if e2e_api_test_exists:
            print("\nWhat would you like to do with the original e2e_api_test.py?")
            print("1. Backup to scripts/e2e_api_test.py.bak")
            print("2. Remove it")
            print("3. Keep it alongside pytest tests")

            try:
                file_choice = int(input("\nEnter your choice (1-3): "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                return

            if file_choice == 1:
                # Backup
                create_directory_if_not_exists("scripts")
                shutil.copy2("e2e_api_test.py", "scripts/e2e_api_test.py.bak")
                print("\nBacked up e2e_api_test.py to scripts/e2e_api_test.py.bak")
            elif file_choice == 2:
                # Ask for confirmation
                confirm = input("\nAre you sure you want to remove e2e_api_test.py? (y/n): ")
                if confirm.lower() == 'y':
                    os.rename("e2e_api_test.py", "e2e_api_test.py.old")
                    print("\nRenamed e2e_api_test.py to e2e_api_test.py.old")
                else:
                    print("\nKeeping e2e_api_test.py")

        print("\nUsing pytest-based API tests")
        print("You can run API tests with: pytest tests/test_api_e2e.py -v")

    elif choice == 3:
        # Keep both approaches
        if not e2e_api_test_exists and pytest_api_test_exists:
            print("\nOnly pytest-based API tests exist. Nothing to do.")
        elif e2e_api_test_exists and not pytest_api_test_exists:
            print("\nOnly e2e_api_test.py exists. Nothing to do.")
        else:
            print("\nKeeping both testing approaches")
            print("For manual testing: python e2e_api_test.py")
            print("For automated testing: pytest tests/test_api_e2e.py -v")

    elif choice == 4:
        print("\nExiting without making changes.")
    else:
        print("\nInvalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main() 