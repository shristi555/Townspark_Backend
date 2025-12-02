from rest_framework.response import Response

"""
Traditional old method threw content not rendered error now trying some big brain moves
"""


def SuccessResponse(
    data=None,
    status=None,
    template_name=None,
    headers=None,
    exception=False,
    content_type=None,
):
    payload = {
        "success": True,
        "response": data or {},
        "error": None,
    }
    return Response(
        payload,
        status=status,
        headers=headers,
        content_type=content_type,
        exception=exception,
        template_name=template_name,
    )


def ErrorResponse(
    error_message="An error occurred",
    error_details=None,
    status=None,
    status_code=None,
    data=None,
    template_name=None,
    headers=None,
    exception=False,
    content_type=None,
):
    """
    Error response model to standardize error responses across the application.
    Args:
        error_message (str): A brief message describing the error.
        error_details (dict or list, optional): Additional details about the error.
        status (int, optional): HTTP status code for the response.
        status_code (int, optional): Alternative HTTP status code for the response just for name convinience can use both status or status_code.
        data (any, optional): Additional data to include in the response.
        template_name (str, optional): Template name for rendering the response.
        headers (dict, optional): Additional headers for the response.
        exception (bool, optional): Whether this response is an exception.
        content_type (str, optional): Content type of the response.
    Returns:
        Response: A DRF Response object with the standardized error format.

    Usage:
        return ErrorResponse(
            error_message="Invalid input data",
            error_details={"field": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    Expected Output:
        {
            "success": False,
            "response": null,
            "error": {
                "message": "Invalid input data",
                "details": {"field": "This field is required."}
            }
        }


    """

    payload = {
        "success": False,
        "response": data,
        "error": {
            "message": error_message,
            "details": error_details,
        },
    }
    return Response(
        payload,
        status=status or status_code,
        headers=headers,
        content_type=content_type,
        exception=exception,
        template_name=template_name,
    )
