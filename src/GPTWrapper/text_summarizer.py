import os
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
                prompt = (
                    "Please summarize the following earnings transcript and extract key insights that investors might find useful. "
                    "Order them as bullet points:\n\n"
                    f"{self.text_content}"
                )
                # Get the summary from the model
                response = self.model(prompt)

                # Extract the text from the AIMessage object
                if hasattr(response, 'content'):
                    self.summary = response.content  # Get the content of the response
                    # Format the summary output, e.g., as bullet points
                    self.summary = self.format_summary(self.summary)  # Format the summary
                    print("Formatted Summary:")
                    print(self.summary)  # For debugging
                else:
                    print("No summary generated.")
            except Exception as e:
                print(f"Error summarizing text: {e}")
        else:
            print("No text content loaded to summarize.")

    def format_summary(self, summary):
        """
        Formats the summary into a bullet point list.
        
        :param summary: The raw summary text.
        :return: Formatted string with bullet points.
        """
        # Split the summary into lines and create bullet points
        bullet_points = summary.split('\n')
        formatted_summary = "\n".join(f"• {point.strip()}" for point in bullet_points if point.strip())
        return formatted_summary

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
