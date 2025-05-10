"""
Service provider for dependency injection.

This module provides a simple service provider for managing dependencies
throughout the application, making it easier to inject dependencies
and improve testability.
"""

import logging
from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar('T')

logger = logging.getLogger("services")

class ServiceProvider:
    """
    Simple service provider for dependency injection.
    
    This class manages service instances and factories for creating
    objects with proper dependencies throughout the application.
    """
    
    def __init__(self):
        """Initialize the service provider."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, service_type: Type[T], implementation: Type[T]) -> None:
        """
        Register a service implementation.
        
        Args:
            service_type: Type/interface for the service
            implementation: Implementation class
            
        Note:
            This registers a type that will be instantiated when needed.
            For factories, use register_factory. For instances, use register_instance.
        """
        key = self._get_type_key(service_type)
        self._services[key] = implementation
        logger.debug(f"Registered service: {key}")
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for a service.
        
        Args:
            service_type: Type/interface for the service
            factory: Factory function that creates instances
        """
        key = self._get_type_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Register an existing instance as a singleton.
        
        Args:
            service_type: Type/interface for the service
            instance: Singleton instance to use
        """
        key = self._get_type_key(service_type)
        self._singletons[key] = instance
        logger.debug(f"Registered instance: {key}")
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service to its implementation.
        
        Args:
            service_type: Type/interface to resolve
            
        Returns:
            Instance of the requested service
            
        Raises:
            KeyError: If the service is not registered
        """
        key = self._get_type_key(service_type)
        
        # Check for singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check for factories
        if key in self._factories:
            # Create from factory and cache as singleton
            instance = self._factories[key]()
            self._singletons[key] = instance
            return instance
        
        # Check for services
        if key in self._services:
            # Create from class and cache as singleton
            instance = self._services[key]()
            self._singletons[key] = instance
            return instance
        
        # Service not found
        raise KeyError(f"Service not registered: {key}")
    
    def has_service(self, service_type: Type[T]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type: Type/interface to check
            
        Returns:
            True if the service is registered, False otherwise
        """
        key = self._get_type_key(service_type)
        return (
            key in self._singletons or 
            key in self._factories or 
            key in self._services
        )
    
    def clear(self) -> None:
        """Clear all registered services and singletons."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("Cleared all services")
    
    def _get_type_key(self, service_type: Type) -> str:
        """
        Get a string key for a type.
        
        Args:
            service_type: Type to convert
            
        Returns:
            String key for the type
        """
        # Handle generic types from typing module by using str(service_type)
        # This handles cases like Factory[T] which don't have a __name__ attribute
        try:
            return f"{service_type.__module__}.{service_type.__name__}"
        except AttributeError:
            # For generic types like Factory[T], use the string representation
            return str(service_type)


# Global service provider instance
service_provider = ServiceProvider()


def get_service(service_type: Type[T]) -> T:
    """
    Get a service from the global service provider.
    
    Args:
        service_type: Type/interface to resolve
        
    Returns:
        Instance of the requested service
    """
    return service_provider.resolve(service_type)


def register_service(service_type: Type[T], implementation: Type[T]) -> None:
    """
    Register a service with the global service provider.
    
    Args:
        service_type: Type/interface for the service
        implementation: Implementation class
    """
    service_provider.register(service_type, implementation)


def register_instance(service_type: Type[T], instance: T) -> None:
    """
    Register an instance with the global service provider.
    
    Args:
        service_type: Type/interface for the service
        instance: Instance to register
    """
    service_provider.register_instance(service_type, instance)


def register_factory(service_type: Type[T], factory: Callable[[], T]) -> None:
    """
    Register a factory with the global service provider.
    
    Args:
        service_type: Type/interface for the service
        factory: Factory function
    """
    service_provider.register_factory(service_type, factory)