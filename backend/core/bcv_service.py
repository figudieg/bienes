import requests
from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation
import urllib3

# Deshabilitar advertencias de certificados SSL no verificados (Sitio BCV)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_tasa_bcv():
    """
    Obtiene la tasa oficial del USD desde el BCV mediante Web Scraping.
    Optimizado con Headers, Timeouts y manejo de errores silencioso.
    """
    url = "https://www.bcv.org.ve/"
    # Valor de respaldo por si la web del BCV está caída (ajustar según mercado)
    tasa_fallback = Decimal("36.50")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    try:
        # Timeout balanceado: 5s para conectar, 10s para leer datos
        response = requests.get(url, headers=headers, verify=False, timeout=(5, 10))
        response.raise_for_status()
        
        # Usamos lxml si está instalado por ser más rápido, si no, html.parser
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # El BCV usa la estructura: <div id="dolar"><strong> 36,50 </strong></div>
        div_dolar = soup.find('div', id='dolar')
        
        if div_dolar:
            strong_tag = div_dolar.find('strong')
            if strong_tag:
                # Limpieza profunda de strings (quitar espacios, saltos de línea y cambiar coma)
                tasa_str = strong_tag.text.strip().replace(',', '.')
                return Decimal(tasa_str).quantize(Decimal("0.01")) # Redondeo a 2 decimales
        
    except (requests.RequestException, InvalidOperation, AttributeError) as e:
        # En producción, podrías loggear esto a un archivo, no solo imprimir
        print(f"⚠️ Alerta BCV: No se pudo obtener tasa real. Usando fallback {tasa_fallback}. Motivo: {e}")
    
    return tasa_fallback
