import chardet

# Check encoding
with open('raw_clean_data/cleaned_case_data.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print("Detected encoding:", result['encoding'])

# Convert to UTF-8 if needed
if result['encoding'] != 'utf-8':
    with open('raw_clean_data/cleaned_case_data.csv', 'r', encoding=result['encoding']) as f:
        content = f.read()
    with open('raw_clean_data/cleaned_case_data.csv', 'w', encoding='utf-8') as f:
        f.write(content)
    print("File re-saved with UTF-8 encoding.")
