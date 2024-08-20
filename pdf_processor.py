import os
import re
import json
import logging
from PyPDF2 import PdfReader

# Setup logging to both file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler('pdf_processing.log')
console_handler = logging.StreamHandler()

# Set logging level for handlers
file_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def extract_repair_order_number_from_pdf(pdf_path):
    """Extracts the repair order number from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            match = re.search(r'Repair Order Number\s*:\s*(\d+)', text)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        return None

def extract_vehicle_and_customer_info(pdf_path):
    """Extracts vehicle info, VIN, customer name, telephone number, and odometer reading from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        vehicle_info = {}
        for page in reader.pages:
            text = page.extract_text()

            # Log the first 500 characters of the extracted text for analysis
            logger.debug(f"Extracted text from {pdf_path}:\n{text[:500]}\n")

            # Extract Vehicle Year, Make, Model, and Odometer Reading
            vehicle_match = re.search(r'Vehicle Information\s*(\d{4})\\(\w+)\\([\w\s-]+)\s*Odometer Reading:\s*([\d,]+)\s*Miles', text)
            vin_match = re.search(r'VIN:\s*([A-HJ-NPR-Z0-9]{17})\s*License Plate:\s*(\w+)', text)
            customer_match = re.search(r'Customer Information\s*Name:\s*([\w\s]+)(?=\sTel|$)', text)
            tel_match = re.search(r'Tel:\s*([\d\-\+\(\)\s]+)', text)

            if vehicle_match:
                logger.debug(f"Vehicle information matched: {vehicle_match.groups()}")
                vehicle_info["year"] = vehicle_match.group(1)
                vehicle_info["make"] = vehicle_match.group(2)
                vehicle_info["model"] = vehicle_match.group(3)
                vehicle_info["odometer_reading"] = vehicle_match.group(4).replace(",", "")
            else:
                logger.warning(f"Vehicle information not found in {pdf_path}")

            if vin_match:
                logger.debug(f"VIN information matched: {vin_match.groups()}")
                vehicle_info["vin"] = vin_match.group(1)
                vehicle_info["license_plate"] = vin_match.group(2)
            else:
                logger.warning(f"VIN information not found in {pdf_path}")

            if customer_match:
                logger.debug(f"Customer information matched: {customer_match.group(1).strip()}")
                vehicle_info["customer_name"] = customer_match.group(1).strip()
            else:
                logger.warning(f"Customer information not found in {pdf_path}")

            if tel_match:
                logger.debug(f"Telephone information matched: {tel_match.group(1).strip()}")
                vehicle_info["telephone"] = tel_match.group(1).strip()
            else:
                vehicle_info["telephone"] = None

            if vehicle_info:
                return vehicle_info
        return None
    except Exception as e:
        logger.error(f"Error extracting vehicle/customer info from {pdf_path}: {e}")
        return None

def determine_scan_type(pdf_path):
    """Determines if the PDF contains a Pre-scan only or both Pre and Post-scan."""
    try:
        reader = PdfReader(pdf_path)
        pre_scan_found = False
        post_scan_found = False

        for page in reader.pages:
            text = page.extract_text()
            if "Pre-scan Report" in text:
                pre_scan_found = True
            if "Post-scan Report" in text:
                post_scan_found = True

        if pre_scan_found and post_scan_found:
            return "pp"  # Both Pre and Post-scan
        elif pre_scan_found:
            return "p"  # Pre-scan only
        else:
            return None
    except Exception as e:
        logger.error(f"Error determining scan type for {pdf_path}: {e}")
        return None

def rename_pdf(pdf_path, repair_order_number, scan_type):
    """Renames the PDF file to the repair order number with the appropriate suffix."""
    directory, original_file_name = os.path.split(pdf_path)
    new_file_name = f"{repair_order_number}{scan_type}.pdf"
    new_file_path = os.path.join(directory, new_file_name)
    
    try:
        os.rename(pdf_path, new_file_path)
        logger.info(f"Renamed: {original_file_name} -> {new_file_name}")
        return new_file_name
    except Exception as e:
        logger.error(f"Error renaming {original_file_name} to {new_file_name}: {e}")
        return None

def create_summary_entry(original_file_name, new_file_name, repair_order_number, vehicle_info, status):
    """Creates a summary entry for a processed PDF file."""
    return {
        "original_filename": original_file_name,
        "new_filename": new_file_name,
        "repair_order_number": repair_order_number,
        "vehicle_info": vehicle_info,  # This includes all the extracted vehicle information
        "status": status
    }



def scan_folder_and_process_pdfs(folder_path, summary_file_path):
    """Scans the folder for PDFs with '~~tmp~~' in their name, processes them, and writes a summary JSON file."""
    total_files = 0
    matching_pdfs = 0
    processed_files = 0
    summary_entries = []
    
    # List all files in the specified directory (non-recursive)
    files = os.listdir(folder_path)
    total_files = len(files)
    
    for file in files:
        if "~~tmp~~" in file and file.endswith('.pdf'):
            matching_pdfs += 1
            pdf_path = os.path.join(folder_path, file)
            directory, original_file_name = os.path.split(pdf_path)
            
            repair_order_number = extract_repair_order_number_from_pdf(pdf_path)
            vehicle_info = extract_vehicle_and_customer_info(pdf_path)
            scan_type = determine_scan_type(pdf_path)
            
            if repair_order_number and scan_type:
                new_file_name = rename_pdf(pdf_path, repair_order_number, scan_type)
                status = "Successfully renamed" if new_file_name else "Error during renaming"
            else:
                new_file_name = None
                status = "Failed to extract required information"
            
            # Create summary entry
            summary_entry = create_summary_entry(original_file_name, new_file_name, repair_order_number, vehicle_info, status)
            summary_entries.append(summary_entry)
            processed_files += 1
    
    # Write the summary JSON file
    with open(summary_file_path, 'w') as summary_file:
        json.dump(summary_entries, summary_file, indent=4)
    
    # Log the summary
    logger.info(f"Total files found: {total_files}")
    logger.info(f"Matching PDF files found: {matching_pdfs}")
    logger.info(f"Total files processed: {processed_files}")

