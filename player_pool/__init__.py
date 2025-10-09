# Player Pool - Automatic Bot Discovery and Import
"""
This module automatically discovers and imports all participant bot classes
from the player_pool directory.

How to add your bot:
1. Create a .py file in the player_pool directory (e.g., my_awesome_bot.py)
2. Define your bot class that inherits from ParentBot
3. The tournament will automatically discover and include your bot!

Example bot file structure:
    player_pool/
    ├── __init__.py (this file)
    ├── alice_bot.py
    ├── bob_strategic_bot.py
    └── charlie_aggressive_bot.py
"""

import os
import importlib
import inspect
from typing import List, Type, Dict, Any
import sys

# Add parent directory to path to import ParentBot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ParentBot import ParentBot

def discover_bot_classes() -> List[Type[ParentBot]]:
    """
    Automatically discover all bot classes in the player_pool directory.
    
    Returns:
        List of bot classes that inherit from ParentBot and implement required methods
    """
    bot_classes = []
    current_dir = os.path.dirname(__file__)
    
    # Get all .py files in the player_pool directory
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'player_pool.{module_name}')
                
                # Find all classes in the module that inherit from ParentBot
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, ParentBot) and 
                        obj != ParentBot and 
                        obj.__module__ == module.__name__):
                        
                        # Validate the bot class
                        validation_result = validate_bot_class(obj, filename)
                        if validation_result["valid"]:
                            bot_classes.append(obj)
                            print(f"Discovered bot: {obj.__name__} from {filename}")
                        else:
                            print(f"Invalid bot {obj.__name__} in {filename}: {validation_result['error']}")
                        
            except Exception as e:
                print(f"Error importing {filename}: {e}")
    
    return bot_classes

def validate_bot_class(bot_class: Type[ParentBot], filename: str) -> Dict[str, Any]:
    """
    Validate that a bot class properly implements the required interface.
    
    Args:
        bot_class: The bot class to validate
        filename: The filename for error reporting
        
    Returns:
        Dict with 'valid' (bool) and 'error' (str) keys
    """
    try:
        # Check if decide_action method is implemented
        if not hasattr(bot_class, 'decide_action'):
            return {"valid": False, "error": "Missing decide_action method"}
        
        # Check if decide_action is callable
        if not callable(getattr(bot_class, 'decide_action')):
            return {"valid": False, "error": "decide_action is not callable"}
        
        # Try to instantiate the bot
        try:
            test_bot = bot_class("ValidationTest", chips=500)
        except Exception as e:
            return {"valid": False, "error": f"Constructor failed: {e}"}
        
        # Check if the bot has required attributes
        required_attrs = ['name', 'chips', 'hand', 'current_bet', 'folded', 'all_in']
        for attr in required_attrs:
            if not hasattr(test_bot, attr):
                return {"valid": False, "error": f"Missing required attribute: {attr}"}
        
        # Test decide_action method with a simple game state
        test_game_state = {
            'current_bet': 10,
            'min_raise': 10,
            'max_raise': 500,
            'pot': 20,
            'community_cards': [],
            'player_bet': 0
        }
        
        try:
            result = test_bot.decide_action(test_game_state)
        except Exception as e:
            return {"valid": False, "error": f"decide_action method failed: {e}"}
        
        # Validate return value format
        if not isinstance(result, tuple) or len(result) != 2:
            return {"valid": False, "error": "decide_action must return tuple (action, amount)"}
        
        action, amount = result
        valid_actions = ['fold', 'check', 'call', 'raise']
        
        if action not in valid_actions:
            return {"valid": False, "error": f"Invalid action '{action}'. Must be one of: {valid_actions}"}
        
        if not isinstance(amount, (int, float)) or amount < 0:
            return {"valid": False, "error": f"Invalid amount '{amount}'. Must be non-negative number"}
        
        # Check for abstract method implementation
        try:
            # This will raise TypeError if abstract methods are not implemented
            test_instance = bot_class("AbstractTest", chips=500)
            # If we get here, all abstract methods are implemented
        except TypeError as e:
            if "abstract" in str(e).lower():
                return {"valid": False, "error": f"Abstract method not implemented: {e}"}
        
        return {"valid": True, "error": None}
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {e}"}

def get_all_bots(starting_chips: int = 500) -> List[ParentBot]:
    """
    Get instances of all discovered bot classes.
    
    Args:
        starting_chips: Starting chip count for each bot
        
    Returns:
        List of bot instances ready for tournament play
    """
    bot_classes = discover_bot_classes()
    bots = []
    
    for bot_class in bot_classes:
        try:
            # Create bot instance with default name (class name)
            bot_name = bot_class.__name__
            bot = bot_class(bot_name, chips=starting_chips)
            bots.append(bot)
            
        except Exception as e:
            print(f"Error creating {bot_class.__name__}: {e}")
    
    return bots

def get_bot_summary() -> str:
    """
    Get a summary of all discovered bots for display purposes.
    
    Returns:
        Formatted string with bot information
    """
    bot_classes = discover_bot_classes()
    
    if not bot_classes:
        return "No participant bots found in player_pool directory."
    
    summary = f"Found {len(bot_classes)} participant bot(s):\n"
    for i, bot_class in enumerate(bot_classes, 1):
        module_file = bot_class.__module__.replace('player_pool.', '') + '.py'
        summary += f"  {i}. {bot_class.__name__} (from {module_file})\n"
    
    return summary

# Auto-discover bots when module is imported
print("Discovering participant bots...")
discovered_bots = discover_bot_classes()

if discovered_bots:
    print(f"Found {len(discovered_bots)} participant bot(s) ready for tournament!")
else:
    print("No participant bots found. Add .py files to player_pool directory.")

# Export discovered classes for easy importing
__all__ = [bot.__name__ for bot in discovered_bots] + ['get_all_bots', 'get_bot_summary', 'discover_bot_classes']