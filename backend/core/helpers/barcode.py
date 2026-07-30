import re

def generate_correlativo_sudebip(next_id):
    """
    Genera un correlativo institucional para la DEM/SUDEBIP.
    Formato: DEM-2026-XXXXX (e.g. DEM-2026-00045)
    """
    return f"DEM-2026-{str(next_id).zfill(5)}"

def get_code128_pattern(char):
    """
    Patrones de barras para Code128 Auto/B.
    Retorna una cadena de 11 bits (e.g. '11011001100' donde 1 es barra y 0 es espacio).
    """
    patterns = {
        ' ': '11011001100', '!': '11001101100', '"': '11001100110',
        '#': '10010011000', '$': '10010001100', '%': '10001001100',
        '&': '10011001000', "'": '10011000100', '(': '10001100100',
        ')': '11001110010', '*': '11001011100', '+': '11001001110',
        ',': '11011100100', '-': '11001110100', '.': '11001110010',
        '/': '11011101100', '0': '11011001110', '1': '11001101110',
        '2': '11001110110', '3': '11001011000', '4': '11001000110',
        '5': '11000101100', '6': '11000100110', '7': '11000110010',
        '8': '11000110100', '9': '11000110010', ':': '11011011000',
        ';': '11011000110', '<': '11000110110', '=': '11010111000',
        '>': '11010001110', '?': '11000101110', '@': '11011101000',
        'A': '11011100010', 'B': '11000111010', 'C': '11010111000',
        'D': '11010001110', 'E': '11000101110', 'F': '11011101000',
        'G': '11011100010', 'H': '11000111010', 'I': '11011101110',
        'J': '11011101110', 'K': '11011110110', 'L': '11101101110',
        'M': '11101100010', 'N': '11101000110', 'O': '11100010110',
        'P': '11100010010', 'Q': '11100001010', 'R': '11100111010',
        'S': '11100110001', 'T': '11100110010', 'U': '11100011010',
        'V': '11100110110', 'W': '11100110010', 'X': '11100110001',
        'Y': '11100110010', 'Z': '11100011010', '[': '11100110110',
        '\\': '11100001101', ']': '11100001101', '^': '11101101110',
        '_': '11101100010', '`': '11101000110', 'a': '11000110001',
        'b': '11000100110', 'c': '11000110010', 'd': '11000110001',
        'e': '11000100110', 'f': '11000110010', 'g': '11000110001',
        'h': '11000110010', 'i': '11000110001', 'j': '11000110010',
        'k': '11010000110', 'l': '11010011110', 'm': '11000101110',
        'n': '11011101000', 'o': '11011100010', 'p': '11000111010',
        'q': '11010111000', 'r': '11010001110', 's': '11000101110',
        't': '11011101000', 'u': '11011100010', 'v': '11000111010',
        'w': '11101101110', 'x': '11101101110', 'y': '11101110110',
        'z': '11101110110', '{': '11101101110', '|': '11101100010',
        '}': '11101000110', '~': '11100010110'
    }
    # Si el caracter no está en el mapa, retorna espacio
    return patterns.get(char, '11011001100')

def text_to_code128_svg(text):
    """
    Genera un código de barras en formato SVG utilizando codificación Code128 (Tipo B).
    Es un generador puro de Python, sin dependencias de librerías externas.
    """
    # Limpiar caracteres que no pertenezcan al rango ASCII imprimible estándar
    text = re.sub(r'[^\x20-\x7E]', '', text)
    
    # 1. Calcular Check Digit (Algoritmo Modulo 103)
    start_value = 104  # Start Code B es el índice 104
    sum_val = start_value
    
    for i, char in enumerate(text):
        char_val = ord(char) - 32  # Los caracteres imprimibles en Code128 B se indexan restando 32 al código ASCII
        sum_val += char_val * (i + 1)
        
    checksum = sum_val % 103
    
    # 2. Construir la cadena de bits del código
    # Inicio Code B (bits start)
    bits = '11010010000'
    
    # Datos
    for char in text:
        bits += get_code128_pattern(char)
        
    # Checksum
    # Mapeo simple de índice checksum a patrón
    checksum_char = chr(checksum + 32)
    bits += get_code128_pattern(checksum_char)
    
    # Stop Code ('1100011101011')
    bits += '1100011101011'
    
    # 3. Renderizar el SVG
    bar_width = 2
    height = 50
    margin = 20
    total_width = len(bits) * bar_width + (margin * 2)
    total_height = height + 40
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" style="background:#fff;">')
    
    # Dibujar las barras
    x = margin
    for bit in bits:
        if bit == '1':
            svg.append(f'  <rect x="{x}" y="{margin}" width="{bar_width}" height="{height}" fill="#000" />')
        x += bar_width
        
    # Dibujar el texto legible debajo
    text_x = total_width / 2
    text_y = height + margin + 20
    svg.append(f'  <text x="{text_x}" y="{text_y}" font-family="Courier, monospace" font-size="14" font-weight="bold" fill="#000" text-anchor="middle">{text}</text>')
    
    svg.append('</svg>')
    
    return "\n".join(svg)
