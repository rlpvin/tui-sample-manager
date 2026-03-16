from sample_manager.app.validators import validate_directory
from sample_manager.db.rating_repository import set_rating
from sample_manager.db.sample_repository import (
    get_all_samples,
    get_sample_count,
    search_samples,
)
from sample_manager.db.tag_repository import add_tag_to_sample
from sample_manager.scanner.directories import (
    get_registered_directories,
    register_directory,
    remove_directory,
)
from sample_manager.scanner.indexer import (
    index_samples,
    remove_deleted_files,
)
from sample_manager.utils.logging import get_logger

logger = get_logger(__name__)


class CommandRouter:

    def route(self, command):

        name = command.name
        args = command.args

        if name == "scan":
            return self.scan()

        if name == "rescan":
            return self.rescan()

        if name == "list":
            return self.list_samples()

        if name == "dirs":
            return self.list_directories()

        if name == "add-dir":
            return self.add_directory(args)

        if name == "rm-dir":
            return self.remove_directory(args)

        if name == "search":
            return self.search(args)

        if name == "tag":
            return self.tag_sample(args)

        if name == "rate":
            return self.rate_sample(args)

        if name == "stats":
            return self.stats()

        raise ValueError(f"Unknown command: {name}")

    # --------------------------------------------------

    def scan(self):

        logger.info("Starting sample scan")

        index_samples()

        logger.info("Scan completed")

        return "Scan completed."

    # --------------------------------------------------

    def rescan(self):

        logger.info("Running rescan")

        remove_deleted_files()
        index_samples()

        return "Rescan completed."

    # --------------------------------------------------

    def list_samples(self):

        samples = get_all_samples()

        if not samples:
            return "No samples indexed."

        return "\n".join(f'{s["id"]} | {s["filename"]}' for s in samples)

    # --------------------------------------------------

    def list_directories(self):

        dirs = get_registered_directories()

        if not dirs:
            return "No directories registered."

        return "\n".join(dirs)

    # --------------------------------------------------

    def add_directory(self, args):

        if not args:
            raise ValueError("add-dir requires a path")

        path = validate_directory(args[0])

        register_directory(path)

        logger.info(f"Registered directory: {path}")

        return f"Directory added: {path}"

    # --------------------------------------------------

    def remove_directory(self, args):

        if not args:
            raise ValueError("rm-dir requires a path")

        path = args[0]

        remove_directory(path)

        return f"Directory removed: {path}"

    # --------------------------------------------------

    def search(self, args):

        if not args:
            raise ValueError("search requires a query")

        query = args[0].lower()

        results = search_samples(query)

        if not results:
            return "No samples found."

        return "\n".join(f'{s["id"]} | {s["filename"]}' for s in results)

    # --------------------------------------------------

    def tag_sample(self, args):

        if len(args) < 2:
            raise ValueError("tag requires: sample_id tag")

        sample_id = int(args[0])
        tag = args[1]

        add_tag_to_sample(sample_id, tag)

        return f"Tag '{tag}' added to sample {sample_id}"

    # --------------------------------------------------

    def rate_sample(self, args):

        if len(args) < 2:
            raise ValueError("rate requires: sample_id rating")

        sample_id = int(args[0])
        rating = int(args[1])

        if rating < 1 or rating > 5:
            raise ValueError("rating must be between 1 and 5")

        set_rating(sample_id, rating)

        return f"Sample {sample_id} rated {rating}/5"

    # --------------------------------------------------

    def stats(self):

        samples = get_sample_count()
        dirs = get_registered_directories()

        return f"Total samples: {samples}\n" f"Directories: {len(dirs)}"
