# Initialize useragents file if it does not exist
def initialize_useragents():
    try:
        open("user-agents.txt", 'x').close()  # Create file if it doesn't exist
    except FileExistsError:
        pass  # File already exists

initialize_useragents()  # Ensure useragents file exists when script is run/imported
