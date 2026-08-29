"""System to manufacturer mapping for ROM organization."""

SYSTEM_MANUFACTURER_MAP = {
    # Nintendo
    'NES': 'Nintendo',
    'SNES': 'Nintendo',
    'N64': 'Nintendo',
    'Game Boy': 'Nintendo',
    'Game Boy Color': 'Nintendo',
    'Game Boy Advance': 'Nintendo',
    'Nintendo DS': 'Nintendo',
    'Wii': 'Nintendo',
    'Wii U': 'Nintendo',
    'Switch': 'Nintendo',
    'GameCube': 'Nintendo',
    'Virtual Boy': 'Nintendo',
    
    # Sega
    'Genesis': 'Sega',
    'Master System': 'Sega',
    'Game Gear': 'Sega',
    'Saturn': 'Sega',
    'Dreamcast': 'Sega',
    '32X': 'Sega',
    
    # Sony
    'PlayStation': 'Sony',
    'PlayStation 2': 'Sony',
    'PlayStation 3': 'Sony',
    'PSP': 'Sony',
    'PS Vita': 'Sony',
    
    # Microsoft
    'Xbox': 'Microsoft',
    'Xbox 360': 'Microsoft',
    'Xbox One': 'Microsoft',
    
    # Atari
    'Atari 2600': 'Atari',
    'Atari 7800': 'Atari',
    'Atari Lynx': 'Atari',
    'Atari Jaguar': 'Atari',
    
    # Other manufacturers
    'Neo Geo': 'SNK',
    'TurboGrafx-16': 'Hudson Soft',
    'PC Engine': 'Hudson Soft',
    'Arcade': 'Various',
    'Commodore 64': 'Commodore',
    'ZX Spectrum': 'Sinclair',
    'Amiga': 'Commodore',
}


def get_manufacturer(system: str) -> str:
    """
    Get manufacturer for a given system.
    
    Args:
        system: System name
        
    Returns:
        Manufacturer name or 'Other' if not found
    """
    return SYSTEM_MANUFACTURER_MAP.get(system, 'Other')
