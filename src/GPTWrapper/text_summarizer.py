import os
import getpass
import constants
from langchain_openai import ChatOpenAI

class TextSummarizer:
    def __init__(self, api_key: str = None, file_path: str = None):
        """
        Initializes the TextSummarizer with an API key and file path.
        
        :param api_key: Optional OpenAI API key. If not provided, it will use the key from constants.
        :param file_path: Path to the text file to summarize.
        """
        # Set OpenAI API key
        self.api_key = api_key or constants.APIKEY
        os.environ["OPENAI_API_KEY"] = self.api_key
        
        # Initialize the ChatOpenAI model
        self.model = ChatOpenAI()

        # Set the file path
        self.file_path = file_path

        # Initialize content and summary
        self.text_content = None
        self.summary = None

    def load_text(self):
        """
        Loads the text from the specified file path.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.text_content = file.read()
            print(f"Successfully loaded content from {self.file_path}")
        except Exception as e:
            print(f"Error loading {self.file_path}: {e}")
            self.text_content = None

    def summarize_text(self):
        """
        Summarizes the loaded text content using the OpenAI model.
        """
        if self.text_content:
            try:
                prompt = f"Please find the key insights out of this earnings transcript which investors might find useful:\n\n{self.text_content}"
                self.summary = self.model(prompt)
                print("Summary:")
                print(self.summary)
            except Exception as e:
                print(f"Error summarizing text: {e}")
        else:
            print("No text content loaded to summarize.")

    def run(self):
        """
        Executes the loading and summarization process.
        """
        self.load_text()
        self.summarize_text()


if __name__ == "__main__":
    # Initialize the TextSummarizer with the desired file path
    summarizer = TextSummarizer(file_path="src/AAPLEarningsTranscript.txt")
    
    # Run the summarization process
    summarizer.run()