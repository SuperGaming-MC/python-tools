#!/usr/bin/env python3
"""
File Password Protection Script - Windows Compatible
No external dependencies required!
"""

import os
import sys
import getpass
import hashlib
import json

# Check Python version
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or higher")
    print(f"You are using Python {sys.version}")
    sys.exit(1)

try:
    import secrets
except ImportError:
    print("Error: 'secrets' module not available. Please use Python 3.6+")
    sys.exit(1)

# Simple XOR-based encryption using built-in libraries only
class SimpleEncryption:
    def __init__(self, key):
        self.key = self._pad_key(key)
    
    def _pad_key(self, key):
        """Pad or truncate key to 32 bytes"""
        if len(key) < 32:
            key += b'0' * (32 - len(key))
        return key[:32]
    
    def encrypt(self, data):
        """Simple XOR-based encryption with key rotation"""
        encrypted = bytearray()
        key_len = len(self.key)
        
        for i, byte in enumerate(data):
            key_byte = self.key[i % key_len]
            encrypted_byte = byte ^ key_byte ^ (i % 256)
            encrypted.append(encrypted_byte)
        
        return bytes(encrypted)
    
    def decrypt(self, encrypted_data):
        """Decrypt the XOR-encrypted data"""
        decrypted = bytearray()
        key_len = len(self.key)
        
        for i, byte in enumerate(encrypted_data):
            key_byte = self.key[i % key_len]
            decrypted_byte = byte ^ key_byte ^ (i % 256)
            decrypted.append(decrypted_byte)
        
        return bytes(decrypted)

class FileProtector:
    def __init__(self):
        self.protected_files_db = "protected_files.json"
        self.load_database()
    
    def load_database(self):
        """Load the database of protected files"""
        try:
            with open(self.protected_files_db, 'r') as f:
                self.protected_files = json.load(f)
        except FileNotFoundError:
            self.protected_files = {}
            print("No existing database found. Creating new one.")
        except Exception as e:
            print(f"Error loading database: {e}")
            self.protected_files = {}
    
    def save_database(self):
        """Save the database of protected files"""
        try:
            with open(self.protected_files_db, 'w') as f:
                json.dump(self.protected_files, f, indent=2)
            print(f"Database saved to {self.protected_files_db}")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        try:
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return key
        except Exception as e:
            print(f"Error deriving key: {e}")
            return None
    
    def encrypt_file(self, file_path: str, password: str):
        """Encrypt a file with password protection"""
        print(f"\n--- Starting encryption process ---")
        print(f"File path: '{file_path}'")
        
        # Normalize the file path for Windows
        file_path = os.path.normpath(file_path)
        print(f"Normalized path: '{file_path}'")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            print(f"Current directory: {os.getcwd()}")
            print("Files in current directory:")
            try:
                for f in os.listdir('.'):
                    print(f"  - {f}")
            except:
                print("  Could not list directory contents")
            return False
        
        # Check if already protected
        if file_path in self.protected_files:
            print(f"File '{file_path}' is already protected.")
            return False
        
        try:
            print("Generating salt...")
            salt = secrets.token_bytes(16)
            print(f"Salt generated: {len(salt)} bytes")
            
            print("Deriving key from password...")
            key = self.derive_key(password, salt)
            if key is None:
                return False
            print("Key derived successfully")
            
            print("Creating encryption cipher...")
            cipher = SimpleEncryption(key)
            
            print(f"Reading file: {file_path}")
            with open(file_path, 'rb') as f:
                file_data = f.read()
            print(f"File read successfully: {len(file_data)} bytes")
            
            print("Encrypting data...")
            encrypted_data = cipher.encrypt(file_data)
            print(f"Data encrypted: {len(encrypted_data)} bytes")
            
            # Create encrypted file path
            encrypted_path = file_path + '.protected'
            print(f"Writing encrypted file: {encrypted_path}")
            
            with open(encrypted_path, 'wb') as f:
                f.write(salt + encrypted_data)
            print("Encrypted file written successfully")
            
            # Verify the encrypted file was created
            if os.path.exists(encrypted_path):
                file_size = os.path.getsize(encrypted_path)
                print(f"Encrypted file created: {encrypted_path} ({file_size} bytes)")
            else:
                print("ERROR: Encrypted file was not created!")
                return False
            
            # Store file info in database
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.protected_files[file_path] = {
                'encrypted_path': encrypted_path,
                'password_hash': password_hash,
                'original_size': len(file_data)
            }
            
            print("Saving database...")
            self.save_database()
            
            print("Removing original file...")
            os.remove(file_path)
            print("Original file removed")
            
            print(f"\n✓ SUCCESS: File '{file_path}' has been encrypted and protected!")
            print(f"✓ Encrypted file: '{encrypted_path}'")
            return True
            
        except PermissionError:
            print(f"ERROR: Permission denied. Cannot write to this location.")
            print("Try running as administrator or choose a different location.")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error during encryption: {e}")
            print(f"Error type: {type(e).__name__}")
            return False
    
    def decrypt_file(self, file_path: str, password: str, temp_access=False):
        """Decrypt a protected file"""
        print(f"\n--- Starting decryption process ---")
        
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        if file_path not in self.protected_files:
            print(f"File '{file_path}' is not in the protected files database.")
            print("Protected files in database:")
            for pf in self.protected_files.keys():
                print(f"  - {pf}")
            return False
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != self.protected_files[file_path]['password_hash']:
            print("❌ Incorrect password!")
            return False
        
        try:
            encrypted_path = self.protected_files[file_path]['encrypted_path']
            print(f"Looking for encrypted file: {encrypted_path}")
            
            if not os.path.exists(encrypted_path):
                print(f"ERROR: Encrypted file '{encrypted_path}' not found.")
                return False
            
            print("Reading encrypted file...")
            with open(encrypted_path, 'rb') as f:
                encrypted_content = f.read()
            print(f"Read {len(encrypted_content)} bytes")
            
            # Extract salt and encrypted data
            salt = encrypted_content[:16]
            encrypted_data = encrypted_content[16:]
            print(f"Salt: {len(salt)} bytes, Encrypted data: {len(encrypted_data)} bytes")
            
            # Derive key and decrypt
            key = self.derive_key(password, salt)
            cipher = SimpleEncryption(key)
            decrypted_data = cipher.decrypt(encrypted_data)
            print(f"Decrypted: {len(decrypted_data)} bytes")
            
            # Write decrypted file
            output_path = file_path + '.temp' if temp_access else file_path
            print(f"Writing to: {output_path}")
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            if temp_access:
                print(f"✓ File temporarily decrypted to: '{output_path}'")
                print("⚠️  Remember to delete the temporary file when done!")
            else:
                print(f"✓ File '{file_path}' has been decrypted and restored.")
                # Remove from protected database and delete encrypted file
                os.remove(encrypted_path)
                del self.protected_files[file_path]
                self.save_database()
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to decrypt file: {e}")
            return False
    
    def delete_protected_file(self, file_path: str, password: str):
        """Delete a protected file after password verification"""
        file_path = os.path.normpath(file_path)
        
        if file_path not in self.protected_files:
            print(f"File '{file_path}' is not in the protected files database.")
            return False
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != self.protected_files[file_path]['password_hash']:
            print("❌ Incorrect password!")
            return False
        
        try:
            encrypted_path = self.protected_files[file_path]['encrypted_path']
            
            # Remove encrypted file
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
                print(f"Encrypted file deleted: {encrypted_path}")
            
            # Remove from database
            del self.protected_files[file_path]
            self.save_database()
            
            print(f"✓ Protected file '{file_path}' has been permanently deleted.")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to delete protected file: {e}")
            return False
    
    def list_protected_files(self):
        """List all protected files"""
        if not self.protected_files:
            print("\n📁 No protected files found.")
            return
        
        print(f"\n📁 Protected Files ({len(self.protected_files)} total):")
        print("-" * 60)
        for file_path, info in self.protected_files.items():
            size_kb = info['original_size'] / 1024
            encrypted_exists = "✓" if os.path.exists(info['encrypted_path']) else "❌"
            print(f"File: {file_path}")
            print(f"  Encrypted as: {info['encrypted_path']} {encrypted_exists}")
            print(f"  Original size: {size_kb:.2f} KB")
            print()

def main():
    print("🔐 File Password Protection System")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    protector = FileProtector()
    
    while True:
        print("\n" + "="*60)
        print("🔐 FILE PASSWORD PROTECTION MENU")
        print("="*60)
        print("1. 🔒 Protect a file (encrypt with password)")
        print("2. 👁️  Open a protected file (temporary access)")
        print("3. 🔓 Restore a protected file (permanent decryption)")
        print("4. 🗑️  Delete a protected file")
        print("5. 📋 List all protected files")
        print("6. 🚪 Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\n🔒 PROTECT A FILE")
            print("-" * 30)
            file_path = input("Enter the file path to protect: ").strip()
            if not file_path:
                print("❌ Please enter a valid file path.")
                continue
            
            # Remove quotes if user added them
            file_path = file_path.strip('"\'')
            
            password = getpass.getpass("🔑 Enter password for this file: ")
            confirm_password = getpass.getpass("🔑 Confirm password: ")
            
            if password != confirm_password:
                print("❌ Passwords don't match!")
                continue
            
            if len(password) < 4:
                print("❌ Password must be at least 4 characters long.")
                continue
            
            protector.encrypt_file(file_path, password)
        
        elif choice == '2':
            print("\n👁️ OPEN PROTECTED FILE")
            print("-" * 30)
            file_path = input("Enter the original file path: ").strip().strip('"\'')
            if not file_path:
                print("❌ Please enter a valid file path.")
                continue
            
            password = getpass.getpass("🔑 Enter password: ")
            protector.decrypt_file(file_path, password, temp_access=True)
        
        elif choice == '3':
            print("\n🔓 RESTORE PROTECTED FILE")
            print("-" * 30)
            file_path = input("Enter the original file path: ").strip().strip('"\'')
            if not file_path:
                print("❌ Please enter a valid file path.")
                continue
            
            password = getpass.getpass("🔑 Enter password: ")
            protector.decrypt_file(file_path, password, temp_access=False)
        
        elif choice == '4':
            print("\n🗑️ DELETE PROTECTED FILE")
            print("-" * 30)
            file_path = input("Enter the original file path to delete: ").strip().strip('"\'')
            if not file_path:
                print("❌ Please enter a valid file path.")
                continue
            
            password = getpass.getpass("🔑 Enter password: ")
            confirm = input("⚠️  Are you sure you want to permanently delete this file? (yes/no): ")
            
            if confirm.lower() == 'yes':
                protector.delete_protected_file(file_path, password)
            else:
                print("❌ Deletion cancelled.")
        
        elif choice == '5':
            protector.list_protected_files()
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
