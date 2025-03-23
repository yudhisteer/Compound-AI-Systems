import logging
import time
from random import random
import requests

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
        backoff_in_seconds: float = 1,
        max_retries: int = 10,
        errors: tuple = (Exception,),
):
    """
    Decorator to retry a function with exponential backoff.
    :param backoff_in_seconds: The initial backoff in seconds.
    :param max_retries: The maximum number of retries.
    :param errors: The errors to catch retry on.
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            # Initialize variables
            num_retries = 0

            # Loop until a successful response or max_retries is hit or an
            # exception is raised
            while True:
                try:
                    print("Attempting to call function")
                    return function(*args, **kwargs)

                # Retry on specified errors
                except errors as e:
                    # Check if max retries has been reached
                    if num_retries > max_retries:
                        raise Exception(f"Maximum number of retries ({max_retries}) exceeded.")

                    # Increment the delay
                    sleep_time = backoff_in_seconds * 2 ** num_retries + random()

                    # Sleep for the delay
                    logger.warning(
                        "%s - %s, retry %s in %s seconds...",
                        e.__class__.__name__,
                        str(e), #Change to str(e) for  example below
                        function.__name__,
                        "{0:.2f}".format(sleep_time),
                    )
                    time.sleep(sleep_time)

                    # Increment retries
                    num_retries += 1

        return wrapper

    return decorator

if __name__ == "__main__":
    # Apply the decorator to a function that might fail temporarily
    @retry_with_exponential_backoff(
        errors=(requests.RequestException,)  # Specify the exact exceptions to catch
    )
    def fetch_data_from_api():
        # Force a failure for the first 2 attempts
        global attempt_count
        if 'attempt_count' not in globals():
            attempt_count = 0
        attempt_count += 1
        
        if attempt_count <= 2:
            # This will trigger the retry mechanism
            raise requests.RequestException("Simulated failure")
        
        # Then succeed on the third attempt
        response = requests.get("https://httpbin.org/get")  
        response.raise_for_status()
        print("Successfully fetched data")
        return response.json()


    data = fetch_data_from_api()
    print(data)
