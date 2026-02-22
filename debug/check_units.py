"""
List available units in PySpice.Unit
"""

from PySpice import Unit

units = [x for x in dir(Unit) if x.startswith('u_')]
print("Available units in PySpice.Unit:")
print(sorted(units))
print()

# Specifically check for length units
length_units = [u for u in units if any(d in u for d in ['m', 'mm', 'cm', 'km', 'inch'])]
print("Length-related units:")
print(length_units)