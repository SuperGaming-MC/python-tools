import os
import shutil
import sys

def delete_path(path):
    """
    Safely delete a file or directory at the given path
    """
    try:
        # Check if path exists
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist.")
            return False
        
        # Check if it's a file or directory
        if os.path.isfile(path):
            os.remove(path)
            print(f"File '{path}' has been deleted successfully.")
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Directory '{path}' and all its contents have been deleted successfully.")
            return True
        else:
            print(f"Error: '{path}' is neither a file nor a directory.")
            return False
            
    except PermissionError:
        print(f"Error: Permission denied. Cannot delete '{path}'.")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False

def main():
    print("=== Path Deletion Tool ===")
    print("WARNING: This will permanently delete the specified file or directory!")
    print("Make sure you have backups of important data.\n")
    
    while True:
        # Get path from user
        path = input("Enter the path to delete (or 'quit' to exit): ").strip()
        
        if path.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not path:
            print("Please enter a valid path.\n")
            continue
        
        # Show what will be deleted
        if os.path.exists(path):
            if os.path.isfile(path):
                file_size = os.path.getsize(path)
                print(f"\nFile to delete: {path}")
                print(f"Size: {file_size} bytes")
            elif os.path.isdir(path):
                try:
                    file_count = sum([len(files) for r, d, files in os.walk(path)])
                    print(f"\nDirectory to delete: {path}")
                    print(f"Contains approximately {file_count} files")
                except:
                    print(f"\nDirectory to delete: {path}")
        else:
            print(f"\nPath does not exist: {path}")
            continue
        
        # Confirm deletion
        confirm = input("\nAre you sure you want to delete this? (yes/no): ").lower()
        
        if confirm in ['yes', 'y']:
            success = delete_path(path)
            if success:
                print("Deletion completed.\n")
            else:
                print("Deletion failed.\n")
        else:
            print("Deletion cancelled.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
