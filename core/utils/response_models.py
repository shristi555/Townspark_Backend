from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


class SuccessResponse(Response):
    """
    Standard success response format for TownSpark API.
    
    Format:
    {
        "success": true,
        "message": "Operation successful",
        "data": { ... },
        "meta": {
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    """
    def __init__(self, data=None, message="Operation successful", status_code=status.HTTP_200_OK, **kwargs):
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "meta": {
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }
        super().__init__(data=response_data, status=status_code, **kwargs)


class ErrorResponse(Response):
    """
    Standard error response format for TownSpark API.
    
    Format:
    {
        "success": false,
        "message": "Error description",
        "errors": {
            "field_name": ["Error message 1", "Error message 2"]
        },
        "error_code": "VALIDATION_ERROR",
        "meta": {
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    """
    def __init__(self, error_message="An error occurred", error_details=None, 
                 error_code="GENERAL_ERROR", status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        response_data = {
            "success": False,
            "message": error_message,
            "errors": error_details or {},
            "error_code": error_code,
            "meta": {
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }
        super().__init__(data=response_data, status=status_code, **kwargs)


class PaginatedResponse(Response):
    """
    Paginated response format for list endpoints.
    """
    def __init__(self, data, count, page, page_size, next_url=None, previous_url=None,
                 message="Data retrieved successfully", status_code=status.HTTP_200_OK, **kwargs):
        total_pages = (count + page_size - 1) // page_size if page_size > 0 else 0
        response_data = {
            "success": True,
            "message": message,
            "data": {
                "results": data,
                "count": count,
                "next": next_url,
                "previous": previous_url,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            },
            "meta": {
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }
        super().__init__(data=response_data, status=status_code, **kwargs)
