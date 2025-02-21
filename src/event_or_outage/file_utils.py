from logging import Logger

class FileUtils:
    logger = Logger('default')
        
    @staticmethod
    def save_markdown(filepath: str, markdown_content: str):
        try:
            with open(filepath, 'w') as f:
                f.write(markdown_content)
            FileUtils.logger.info(f"Charts generated at {filepath}")
        except IOError as e:
            raise IOError(f"Could not open file {filepath} for writing: {str(e)}")