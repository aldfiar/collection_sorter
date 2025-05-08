"""
This module has been deprecated. Use the ZipCommandHandler from
cli_handlers.zip_handler instead.

This stub module remains only for backward compatibility with tests and will be removed
in a future version.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The mass_zip module is deprecated. Use the ZipCommandHandler from "
    "cli_handlers.zip_handler instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import the new implementation for backward compatibility
from collection_sorter.cli_handlers.zip_handler import ZipCommandHandler

# For backward compatibility with tests
def zip_collections(*args, **kwargs):
    """
    Deprecated function. Use ZipCommandHandler instead.
    """
    warnings.warn(
        "zip_collections is deprecated. Use ZipCommandHandler.handle() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Extract args that were used in the old API
    if len(args) > 0:
        kwargs['sources'] = args[0] if isinstance(args[0], list) else [args[0]]
    
    # Create and execute the handler
    handler = ZipCommandHandler(**kwargs)
    handler.handle()

# Legacy class for tests
class ZipCollections:
    """
    Legacy class for backward compatibility with tests.
    """
    
    def __init__(self, archive=False, destination=None):
        warnings.warn(
            "ZipCollections is deprecated. Use ZipCommandHandler instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.archive = archive
        self.destination = destination
    
    def execute(self, source_path):
        # Use the new handler
        handler = ZipCommandHandler(
            sources=[str(source_path)],
            destination=self.destination,
            archive=self.archive
        )
        
        result = handler.handle()
        
        # Preserve exception behavior
        if result.is_failure():
            error = result.error()
            if "FILE_NOT_FOUND" in str(error):
                raise FileNotFoundError(f"Source path does not exist: {source_path}")
            else:
                raise Exception(str(error))

# Legacy function for tests
def parse_args(args=None):
    """
    Parse command-line arguments for legacy tests.
    """
    import argparse
    
    warnings.warn(
        "parse_args is deprecated. Use Click commands instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    parser = argparse.ArgumentParser(description="Archive directories")
    parser.add_argument("sources", nargs="+", help="Source directories to archive")
    parser.add_argument("-d", "--destination", help="Destination directory")
    parser.add_argument("-a", "--archive", action="store_true", help="Create nested archives")
    parser.add_argument("-m", "--move", action="store_true", help="Remove source files after processing")
    
    return parser.parse_args(args)