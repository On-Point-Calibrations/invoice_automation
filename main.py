import os
from datetime import datetime
from pdf_processor import scan_folder_and_process_pdfs

def main():
    # Get the current working directory
    current_path = os.getcwd()
    
    # Print the current directory and ask for confirmation or a new path
    print(f"Current working directory: {current_path}")
    user_input = input("Provide folder path to process PDFs, or leave empty to use current working directory: ").strip()

    # Determine the folder path based on user input
    if user_input == '':
        folder_path = current_path
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
