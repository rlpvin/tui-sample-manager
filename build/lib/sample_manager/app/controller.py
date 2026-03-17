from sample_manager.app.parser import parse_command
from sample_manager.app.router import CommandRouter
from sample_manager.utils.logging import get_logger, setup_logging


class ApplicationController:

    def __init__(self):

        setup_logging()

        self.logger = get_logger(__name__)

        self.router = CommandRouter()

    def handle_input(self, input_line: str):

        try:

            command = parse_command(input_line)

            result = self.router.route(command)

            return result

        except Exception as e:

            self.logger.error(str(e))

            return f"Error: {e}"
