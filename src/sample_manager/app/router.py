from sample_manager.app.validators import validate_directory
from sample_manager.db.rating_repository import remove_rating, set_rating
from sample_manager.db.sample_repository import (
    get_all_samples,
    get_sample_count,
    search_samples,
)
from sample_manager.db.tag_repository import (
    add_tag_to_sample,
    get_all_tags,
    remove_tag_from_sample,
)
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

        if name == "unrate":
            return self.unrate_sample(args)

        if name == "untag":
            return self.untag_sample(args)

        if name == "tags":
            return self.list_tags()

        if name == "bulk-tag":
            return self.bulk_tag(args)

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

        results = search_samples({"query": query})

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

    def untag_sample(self, args):

        if len(args) < 2:
            raise ValueError("untag requires: sample_id tag")

        sample_id = int(args[0])
        tag = args[1]

        remove_tag_from_sample(sample_id, tag)

        return f"Tag '{tag}' removed from sample {sample_id}"

    # --------------------------------------------------

    def list_tags(self):

        tags = get_all_tags()

        if not tags:
            return "No tags created yet."

        return ", ".join(tags)

    # --------------------------------------------------

    def bulk_tag(self, args):
        """
        bulk-tag <query> <tag>
        Note: This is a simplified version. TUI handles complex parsing.
        """
        if len(args) < 2:
            raise ValueError("bulk-tag requires: query tag")

        query = args[0]
        tag = args[1]

        # Use search_samples with simple query
        samples = search_samples({"query": query})

        for s in samples:
            add_tag_to_sample(s["id"], tag)

        return f"Added tag '{tag}' to {len(samples)} samples matching '{query}'."

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

    def unrate_sample(self, args):

        if not args:
            raise ValueError("unrate requires: sample_id")

        sample_id = int(args[0])

        remove_rating(sample_id)

        return f"Rating removed for sample {sample_id}"

    # --------------------------------------------------

    def stats(self):

        samples = get_sample_count()
        dirs = get_registered_directories()

        return f"Total samples: {samples}\n" f"Directories: {len(dirs)}"
