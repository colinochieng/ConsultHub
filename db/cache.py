#!/usr/bin/env python3
"""
Module for Caching (Uses Redis)
"""
import os
import redis


config_r = {
    "host": os.getenv("REDIS_HOST", "127.0.0.1"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "decode_responses": True,
}


class RedisConnect:
    """
    class for connecting to the redis database
    """

    def __init__(self) -> None:
        self.__redis_instance = redis.StrictRedis(**config_r)

    def get(self, key: str) -> str | None:
        """
        A method to retrive the key from database
        Args:
            key (str): key to search for
        Note Key must be a string otherwise the process will raise an error
        """
        if type(key) is not str:
            raise TypeError("RedisConnect search key must be a string")

        return self.__redis_instance.get(key)

    def set(self, key, value) -> bool:
        """
        A method to set the key-value from database
        Args:
            key (str): key to set for
            value (str): value of key in redis
        Return: True if key was set else false
        Note: Key or Value must be strings otherwise
            the process will raise an error
        """
        if type(key) is not str and type(value) is not str:
            raise TypeError("RedisConnect key and value must be strings")

        ttl = 3600 * 60 * 60
        return True if self.__redis_instance.setex(key, ttl, value) else False

    def delete(self, key) -> bool:
        """
        A method to delete the key from database
        Args:
            key (str): key to delete
        return: True if key was deleted else false (Key not exists)
        Note Key must be a string otherwise the process will raise an error
        """
        if type(key) is not str:
            raise TypeError("RedisConnect delete key must be a string")

        return bool(self.__redis_instance.delete(key))

    def close(self) -> None:
        """
        A method to close redis instance connection
        """
        self.__redis_instance.close()
