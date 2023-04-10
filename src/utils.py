__all__ = ["save_file_to_cloud_mock"]


def save_file_to_cloud_mock(url: str, html: str) -> None:
    """
    Mocks the upload a document to the cloud storage

    :param url: the document URL
    :param html: the document HTML content
    """
    print(f"Url: {url} was saved to the cloud.")
