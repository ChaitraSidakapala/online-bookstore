"""HTTP Client for communicating with Catalog Service."""
import os
import httpx
from typing import Optional
from decimal import Decimal


# Get Catalog Service URL from environment variable
CATALOG_SERVICE_URL = os.getenv(
    "CATALOG_SERVICE_URL",
    "http://catalog-service:8000"
)


class CatalogClient:
    """Client for interacting with the Catalog Service API."""
    
    def __init__(self, base_url: str = CATALOG_SERVICE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = 10.0
    
    async def get_book(self, book_id: int) -> Optional[dict]:
        """
        Get book details from Catalog Service.
        
        Args:
            book_id: The ID of the book to retrieve
            
        Returns:
            Book data as dictionary or None if not found
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/books/{book_id}")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
            
            except httpx.TimeoutException:
                raise Exception("Catalog service is unavailable (timeout)")
            except httpx.HTTPError as e:
                raise Exception(f"Failed to communicate with catalog service: {str(e)}")
    
    async def check_availability(self, book_id: int, required_quantity: int) -> tuple[bool, Optional[dict], Optional[str]]:
        """
        Check if a book is available in the required quantity.
        
        Args:
            book_id: The ID of the book
            required_quantity: The quantity needed
            
        Returns:
            Tuple of (is_available, book_data, error_message)
        """
        try:
            book = await self.get_book(book_id)
            
            if book is None:
                return False, None, f"Book with ID {book_id} not found"
            
            available_quantity = book.get('quantity', 0)
            
            if available_quantity < required_quantity:
                return False, book, f"Insufficient stock. Available: {available_quantity}, Required: {required_quantity}"
            
            return True, book, None
        
        except Exception as e:
            return False, None, str(e)
    
    async def update_book_quantity(self, book_id: int, new_quantity: int) -> bool:
        """
        Update book quantity in the catalog (for inventory management).
        
        Args:
            book_id: The ID of the book
            new_quantity: The new quantity value
            
        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.put(
                    f"{self.base_url}/books/{book_id}",
                    json={"quantity": new_quantity}
                )
                response.raise_for_status()
                return True
            
            except httpx.HTTPError:
                return False


# Global catalog client instance
catalog_client = CatalogClient()
