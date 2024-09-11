from rest_framework import renderers


class UserRenderer(renderers.JSONRenderer):
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        # Initialize response
        response = {}

        # Check if the data contains errors
        if isinstance(data, dict) and "errors" in data:
            response["errors"] = data["errors"]
        else:
            # Wrap the response data with a "user" key if needed
            response["user"] = data

        # Serialize the response to JSON
        return super().render(response, media_type, renderer_context)
