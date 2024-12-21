import streamlit as st
from pyzxing import BarCodeReader
from PIL import Image
import pandas as pd
import isbnlib
import pyheif
import io

# Initialize the data storage
if "book_data" not in st.session_state:
    st.session_state["book_data"] = []

# Function to detect barcode using pyzxing
def detect_barcode(image):
    reader = BarCodeReader()
    result = reader.decode(image)
    if result and "parsed" in result[0]:
        return result[0]["parsed"]
    return None

# Function to convert HEIC to JPEG
def convert_heic_to_jpeg(heic_file):
    heif_file = pyheif.read(heic_file)
    image = Image.frombytes(
        heif_file.mode, heif_file.size, heif_file.data, heif_file.stride
    )
    return image

# Title and Instructions
st.title("📚 Home Library Scanner")
st.write("Use your phone to scan book barcodes and build your library list.")

# File uploader to upload images
uploaded_file = st.file_uploader("Upload barcode image", type=["jpg", "png", "jpeg", "heic"])

if uploaded_file:
    # If the file is in HEIC format, convert it
    if uploaded_file.name.lower().endswith(".heic"):
        image = convert_heic_to_jpeg(uploaded_file)
    else:
        # Otherwise, load the image normally
        image = Image.open(uploaded_file)
    
    # Detect barcode from the image
    isbn_raw = detect_barcode(image)
    
    if isbn_raw:
        # Decode if ISBN is in bytes
        isbn = isbn_raw.decode("utf-8") if isinstance(isbn_raw, bytes) else isbn_raw
        st.write(f"Detected ISBN: {isbn}")
        
        # Fetch book details
        try:
            book = isbnlib.meta(isbn)
            if book:
                book_data = {
                    "ISBN": isbn,
                    "Title": book.get("Title", "Unknown"),
                    "Author": ", ".join(book.get("Authors", ["Unknown"])),
                    "Genre": book.get("Subjects", "Unknown"),
                }
                st.session_state["book_data"].append(book_data)
                st.success(f"Added: {book_data['Title']} by {book_data['Author']}")
            else:
                st.warning(f"No details found for ISBN: {isbn}")
        except Exception as e:
            st.error(f"Error fetching details: {e}")
    else:
        st.warning("No barcode detected in the image.")

# Show the current library
if st.session_state["book_data"]:
    st.write("### Your Library")
    df = pd.DataFrame(st.session_state["book_data"])
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "library.csv", "text/csv")

# Run instructions
st.write("Run this app on your computer and open the URL on your phone for seamless scanning.")
