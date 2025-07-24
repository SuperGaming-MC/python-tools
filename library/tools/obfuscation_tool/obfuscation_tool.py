#!/usr/bin/env python3
"""
Interactive File/Folder Obfuscation Tool
Provides XOR-based obfuscation for files and directories
"""

import os
import sys
import hashlib
from pathlib import Path

def derive_key(password, length=256):
    """Derive a key from password using SHA-256"""
    key = hashlib.sha256(password.encode()).digest()
    # Extend key to desired length
    extended_key = (key * ((length // len(key)) + 1))[:length]
    return extended_key

def xor_data(data, key):
    """XOR data with key (cycling through key as needed)"""
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))

def obfuscate_file(file_path, password):
    """Obfuscate a single file and delete the original"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        key = derive_key(password)
        obfuscated_data = xor_data(data, key)
        
        # Add .obf extension
        output_path = file_path + '.obf'
        with open(output_path, 'wb') as f:
            f.write(obfuscated_data)
        
        # Delete the original file after successful obfuscation
        os.remove(file_path)
        
        print(f"✓ Obfuscated and replaced: {file_path} -> {output_path}")
        return True
    except Exception as e:
        print(f"✗ Error obfuscating {file_path}: {e}")
        # If obfuscation failed, don't delete the original
        return False

def deobfuscate_file(file_path, password):
    """Deobfuscate a single file and delete the obfuscated version"""
    try:
        if not file_path.endswith('.obf'):
            print(f"✗ Warning: {file_path} doesn't have .obf extension")
        
        with open(file_path, 'rb') as f:
            obfuscated_data = f.read()
        
        key = derive_key(password)
        original_data = xor_data(obfuscated_data, key)
        
        # Remove .obf extension for output
        if file_path.endswith('.obf'):
            output_path = file_path[:-4]
        else:
            output_path = file_path + '.deobf'
        
        with open(output_path, 'wb') as f:
            f.write(original_data)
        
        # Delete the obfuscated file after successful deobfuscation
        os.remove(file_path)
        
        print(f"✓ Deobfuscated and replaced: {file_path} -> {output_path}")
        return True
    except Exception as e:
        print(f"✗ Error deobfuscating {file_path}: {e}")
        # If deobfuscation failed, don't delete the obfuscated file
        return False

def process_folder(folder_path, password, operation):
    """Process all files in a folder"""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"✗ Folder doesn't exist: {folder_path}")
        return False
    
    if not folder.is_dir():
        print(f"✗ Path is not a directory: {folder_path}")
        return False
    
    success_count = 0
    total_count = 0
    
    # Get all files recursively
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            total_count += 1
            if operation == 'obfuscate':
                # Skip already obfuscated files
                if not str(file_path).endswith('.obf'):
                    if obfuscate_file(str(file_path), password):
                        success_count += 1
            elif operation == 'deobfuscate':
                # Only process .obf files
                if str(file_path).endswith('.obf'):
                    if deobfuscate_file(str(file_path), password):
                        success_count += 1
    
    print(f"\nProcessed {success_count}/{total_count} files successfully")
    return success_count > 0

def get_password():
    """Get password from user with confirmation for obfuscation"""
    import getpass
    
    password = getpass.getpass("Enter password: ")
    if not password:
        print("✗ Password cannot be empty")
        return None
    
    return password

def confirm_password():
    """Get and confirm password for obfuscation"""
    import getpass
    
    password1 = getpass.getpass("Enter password: ")
    if not password1:
        print("✗ Password cannot be empty")
        return None
    
    password2 = getpass.getpass("Confirm password: ")
    if password1 != password2:
        print("✗ Passwords don't match")
        return None
    
    return password1

def main_menu():
    """Display main menu and get user choice"""
    print("\n" + "="*50)
    print("    FILE/FOLDER OBFUSCATION TOOL")
    print("="*50)
    print("1. Obfuscate a file")
    print("2. Deobfuscate a file")
    print("3. Obfuscate a folder")
    print("4. Deobfuscate a folder")
    print("5. Exit")
    print("-"*50)
    
    while True:
        try:
            choice = input("Select option (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("Please enter a number between 1 and 5")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
        except EOFError:
            print("\n\nExiting...")
            sys.exit(0)

def get_file_path(prompt):
    """Get file path from user with validation"""
    while True:
        path = input(prompt).strip()
        if not path:
            print("✗ Path cannot be empty")
            continue
        
        # Remove quotes if present
        path = path.strip('"\'')
        
        if os.path.exists(path):
            return path
        else:
            print(f"✗ Path doesn't exist: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None

def main():
    """Main program loop"""
    print("Welcome to the File/Folder Obfuscation Tool!")
    print("This tool uses XOR encryption for basic file obfuscation.")
    
    while True:
        try:
            choice = main_menu()
            
            if choice == 5:
                print("Goodbye!")
                break
            
            # Get file/folder path
            if choice in [1, 2]:
                path_prompt = "Enter file path: "
            else:
                path_prompt = "Enter folder path: "
            
            path = get_file_path(path_prompt)
            if not path:
                continue
            
            # Get password
            if choice in [1, 3]:  # Obfuscation
                password = confirm_password()
                if not password:
                    continue
                print(f"\n{'Obfuscating'} {'file' if choice == 1 else 'folder'}...")
            else:  # Deobfuscation
                password = get_password()
                if not password:
                    continue
                print(f"\n{'Deobfuscating'} {'file' if choice == 2 else 'folder'}...")
            
            # Perform operation
            success = False
            if choice == 1:
                success = obfuscate_file(path, password)
            elif choice == 2:
                success = deobfuscate_file(path, password)
            elif choice == 3:
                success = process_folder(path, password, 'obfuscate')
            elif choice == 4:
                success = process_folder(path, password, 'deobfuscate')
            
            if success:
                print("\n✓ Operation completed successfully!")
            else:
                print("\n✗ Operation failed or completed with errors")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
