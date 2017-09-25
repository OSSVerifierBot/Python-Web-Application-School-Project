"""Represent condition of an inator.

This module contains a class that represents the condition of an inator.

Refer to Python's documentation for the `enum
<https://docs.python.org/3.5/library/enum.html>`_ module for details
on how to use the class.

"""
import enum


class Condition(enum.IntEnum):
    """Represent the condition of an inator."""

    HOPELESSLY_BROKEN = 1
    NEEDS_REPAIR = 2
    KINDA_WORKS = 3
    USUALLY_WORKS = 4
    ACTUALLY_WORKS = 5
