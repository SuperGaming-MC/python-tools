import zlib
import sys

# ANSI color codes for fun terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("PNG Metadata Steganography Tool")
    print("Hide and reveal secret messages inside PNG files' metadata!")
    print(f"{Colors.ENDC}")

def add_text_chunk(png_path, output_path, key, text):
    try:
        with open(png_path, 'rb') as f:
            data = f.read()

        ihdr_end = 8 + 25  # PNG header + IHDR chunk

        text_data = key.encode() + b'\x00' + text.encode()
        length = len(text_data)
        chunk_type = b'tEXt'
        crc = zlib.crc32(chunk_type + text_data)
        chunk = length.to_bytes(4, 'big') + chunk_type + text_data + crc.to_bytes(4, 'big')

        new_data = data[:ihdr_end] + chunk + data[ihdr_end:]

        with open(output_path, 'wb') as f:
            f.write(new_data)

        print(f"{Colors.OKGREEN}✅ Message hidden successfully in {output_path}!{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")

def read_text_chunks(png_path):
    try:
        with open(png_path, 'rb') as f:
            data = f.read()

        pos = 8  # skip PNG header
        texts = []
        while pos < len(data):
            length = int.from_bytes(data[pos:pos+4], 'big')
            chunk_type = data[pos+4:pos+8]
            chunk_data = data[pos+8:pos+8+length]
            if chunk_type == b'tEXt':
                try:
                    key_text = chunk_data.split(b'\x00', 1)
                    key = key_text[0].decode()
                    text = key_text[1].decode()
                    texts.append((key, text))
                except:
                    pass
            pos += length + 12
        return texts
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return []

def menu():
    print(f"""
{Colors.HEADER}Choose your adventure:{Colors.ENDC}
1️⃣  Hide a secret message inside a PNG
2️⃣  Reveal secret messages from a PNG
3️⃣  Exit
""")

def main():
    print_banner()
    while True:
        menu()
        choice = input(f"{Colors.OKBLUE}Your choice → {Colors.ENDC}").strip()
        if choice == '1':
            png_in = input("📂 Enter path to your PNG image: ").strip()
            png_out = input("💾 Enter output PNG file name: ").strip()
            key = input("🔑 Enter a key (tag) for your secret message (e.g. 'secret'): ").strip()
            message = input("📝 Enter your secret message: ").strip()
            add_text_chunk(png_in, png_out, key, message)
        elif choice == '2':
            png_in = input("📂 Enter path to PNG image to reveal messages: ").strip()
            secrets = read_text_chunks(png_in)
            if secrets:
                print(f"{Colors.OKGREEN}🔍 Found the following secret messages:{Colors.ENDC}")
                for i, (k, msg) in enumerate(secrets, 1):
                    print(f" {i}. [{Colors.BOLD}{k}{Colors.ENDC}]: {msg}")
            else:
                print(f"{Colors.WARNING}⚠️ No secret messages found in this PNG.{Colors.ENDC}")
        elif choice == '3':
            print(f"{Colors.OKCYAN}👋 Thanks for using the Stego Tool! Goodbye!{Colors.ENDC}")
            sys.exit()
        else:
            print(f"{Colors.WARNING}❓ Invalid choice, try again.{Colors.ENDC}")

if __name__ == "__main__":
    main()
