# Validation Framework Guide

This document explains how to use the new validation framework in the processors package to ensure robust parameter validation in file processing operations.

## Overview

The validation framework provides a structured approach to validating parameters for file processors. It uses a combination of:

1. **Validators**: Classes that validate specific types of parameters
2. **ValidationResult**: A generic class that holds validation status and errors
3. **ProcessorValidators**: Classes that validate all parameters for a specific processor

## Basic Usage

### Using Existing Processors

When using the existing processor classes, validation happens automatically:

```python
from collection_sorter.templates.processors import RenameProcessorTemplate
from collection_sorter.result import Result

# Create the processor - validation happens during initialization
processor = RenameProcessorTemplate(
    source_path="/path/to/source",
    destination_path="/path/to/destination",
    patterns={"pattern": "replacement"}
)

# Execute the processor - any validation errors will be returned as failures
result = processor.execute()
if result.is_failure():
    # Handle validation errors
    errors = result.error()
    for error in errors:
        print(f"Error: {error.message}")
else:
    # Process successful
    stats = result.unwrap()
    print(f"Processed {stats['processed']} files")
```

### Creating Custom Validators

You can create custom validators by extending the base `Validator` class:

```python
from collection_sorter.templates.processors.base import Validator, ValidationResult
from typing import Any, Dict

class CustomValidator(Validator):
    def validate(self, value: Any) -> ValidationResult[Dict]:
        # Implement validation logic
        if not isinstance(value, dict):
            return ValidationResult.failure("Value must be a dictionary")
            
        # Additional validation...
        
        return ValidationResult.success(value)
```

### Creating Custom Processor Validators

For complex validation logic, extend the `BaseProcessorValidator`:

```python
from collection_sorter.templates.processors.base import BaseProcessorValidator, ValidationResult
from collection_sorter.result import Result, OperationError, ErrorType
from typing import Any, Dict, List

class CustomProcessorValidator(BaseProcessorValidator):
    def validate_parameters(self, **kwargs) -> Result[Dict[str, Any], List[OperationError]]:
        # First call the base class validator
        base_result = super().validate_parameters(**kwargs)
        if base_result.is_failure():
            return base_result
            
        validated = base_result.unwrap()
        errors = []
        
        # Add your custom validation logic
        custom_param_result = self._validate_custom_param(kwargs.get('custom_param'))
        if not custom_param_result:
            errors.append(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message=f"Invalid custom parameter: {'; '.join(custom_param_result.errors)}"
            ))
        else:
            validated['custom_param'] = custom_param_result.value
            
        # Return validation result
        if errors:
            return Result.failure(errors)
        return Result.success(validated)
        
    def _validate_custom_param(self, value) -> ValidationResult:
        # Implement validation for a specific parameter
        # ...
```

## Creating Custom Processors with Validation

To create a custom processor with validation:

```python
from collection_sorter.templates.processors.base import BaseFileProcessor
from collection_sorter.result import Result, OperationError, ErrorType
from typing import Any, Dict, List, Union
from pathlib import Path

class CustomProcessor(BaseFileProcessor):
    def __init__(
        self,
        source_path: Union[str, Path],
        destination_path: Union[str, Path],
        custom_param: Any,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler = None
    ):
        # Create a custom validator
        validator = CustomProcessorValidator()
        
        # Initialize the base class with the validator
        super().__init__(
            source_path=source_path,
            destination_path=destination_path,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler,
            validator=validator
        )
        
        # Store custom parameters
        self.custom_param = custom_param
        
    def _execute_implementation(self) -> Result[Dict[str, Any], List[OperationError]]:
        # Implement processor-specific logic
        # ...
```

## Available Validators

### PathValidator
Validates file paths with options:
- `must_exist`: Whether the path must exist
- `must_be_dir`: Whether the path must be a directory
- `must_be_file`: Whether the path must be a file
- `create_if_missing`: Whether to create the path if it doesn't exist

### ExtensionsValidator
Validates file extensions with options:
- `valid_extensions`: Set of valid file extensions to allow

### PatternValidator
Validates rename patterns (regex to replacement mapping)

## Best Practices

1. **Early Validation**: Always validate parameters as early as possible, typically at initialization time
2. **Clear Error Messages**: Include specific details in error messages to help diagnose issues
3. **Type Safety**: Use type hints and validation to ensure parameters have the correct types
4. **Fail Fast**: Return validation errors immediately rather than continuing with invalid parameters
5. **Layer Validation**: Start with general validation and then add specific validation checks

## Error Handling

The validation framework integrates with the Result pattern for consistent error handling:

```python
# Handle execution results
result = processor.execute()
if result.is_failure():
    errors = result.error()
    for error in errors:
        if error.type == ErrorType.VALIDATION_ERROR:
            # Handle validation error
            print(f"Validation error: {error.message}")
        else:
            # Handle other error
            print(f"Operation error: {error.message}")
else:
    # Success case
    data = result.unwrap()
    print(f"Success: {data}")
```

## Testing Validation

When testing processors, make sure to:

1. Test valid and invalid inputs
2. Verify error messages are clear and helpful
3. Test edge cases like empty values, None values, etc.
4. Test that failures from validation are properly propagated