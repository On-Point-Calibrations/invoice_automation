import os
from datetime import datetime
from pdf_processor import scan_folder_and_process_pdfs

def get_default_path():
    """Reads the default path from 'default_path.txt', ignoring empty lines and comments."""
    try:
        with open('default_path.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if os.path.isdir(line):
                        return line
                    else:
                        print(f"Warning: The path in 'default_path.txt' does not exist: {line}")
                        return None
        print("Error: No valid paths found in 'default_path.txt'.")
        return None
    except FileNotFoundError:
        print("Error: 'default_path.txt' not found.")
        return None

def main():
    # Get the default path from the file
    default_path = get_default_path()
    if not default_path:
        default_path = os.getcwd()  # Fallback to current working directory if the file is missing or path is invalid

    # Prompt user with the default path
    print(f"Default folder path: {default_path}")
    user_input = input("Press Enter to use the default path, or provide a different folder path: ").strip()

    # Determine the folder path based on user input
    if user_input == '':
        folder_path = default_path
    else:
        # Strip quotation marks if they are present
        folder_path = user_input.strip('"').strip("'")

    # Check if the path exists
    if not os.path.isdir(folder_path):
        print(f"Error: The folder path '{folder_path}' does not exist.")
        return

    # Generate a timestamp for the summary filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file_name = f"summary_{timestamp}.json"
    summary_file_path = os.path.join(folder_path, summary_file_name)
    
    # Call the function to process PDFs and generate the summary
    scan_folder_and_process_pdfs(folder_path, summary_file_path)

    # Ask the user if they want to delete the summary file
    delete_summary = input(f"Processing complete. Do you want to delete the summary file ({summary_file_name})? (y/n): ").strip().lower()
    
    if delete_summary == 'y':
        try:
            os.remove(summary_file_path)
            print("Summary file deleted.")
        except Exception as e:
            print(f"Error deleting summary file: {e}")
    else:
        print(f"Summary file retained at: {summary_file_path}")

if __name__ == "__main__":
    main()