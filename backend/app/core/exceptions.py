"""Custom exceptions for FactLens domain."""

class FactLensException(Exception):
    """Base exception for FactLens application."""
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.detail = detail


class DocumentNotFoundError(FactLensException):
    """Raised when a requested document ID does not exist."""
    pass


class DuplicateDocumentError(FactLensException):
    """Raised when attempting to upload a document with an identical SHA-256 hash."""
    def __init__(self, message: str, existing_document_id: str = ""):
        super().__init__(message)
        self.existing_document_id = existing_document_id


class InvalidPDFError(FactLensException):
    """Raised when an uploaded file is not a valid PDF or is corrupted."""
    pass


class DocumentProcessingError(FactLensException):
    """Raised when PDF extraction, grounding or parsing fails."""
    pass


class FactExtractionError(FactLensException):
    """Raised when fact extraction fails or yields unrecoverable parse errors."""
    pass


class LLMProviderError(FactLensException):
    """Raised when the configured LLM provider encounters an error."""
    pass


class GroundingVerificationError(FactLensException):
    """Raised when an extracted fact fails strict evidence grounding."""
    pass
