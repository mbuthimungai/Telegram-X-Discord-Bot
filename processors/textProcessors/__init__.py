

# Initialize blacklist file if it does not exist
def initialize_blacklist():
    try:
        open("blacklist.txt", 'x').close()  # Create file if it doesn't exist
    except FileExistsError:
        pass  # File already exists

initialize_blacklist()  # Ensure blacklist file exists when script is run/imported
