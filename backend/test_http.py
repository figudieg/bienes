import requests
import time

url_login = "http://127.0.0.1:8000/api/users/auth/login/"
url_bienes = "http://127.0.0.1:8000/api/inventario/bienes/"

try:
    print("Iniciando login HTTP...")
    t0 = time.time()
    res_login = requests.post(url_login, json={"username": "operador", "password": "Password123!"})
    print("Login status:", res_login.status_code)
    print("Login time:", time.time() - t0, "seconds")
    
    if res_login.status_code == 200:
        token = res_login.json()['access']
        print("Token obtenido con éxito.")
        
        headers = {"Authorization": f"Bearer {token}"}
        print("Realizando petición a /api/inventario/bienes/...")
        t0 = time.time()
        res_bienes = requests.get(url_bienes, headers=headers)
        print("Bienes status:", res_bienes.status_code)
        print("Bienes query time:", time.time() - t0, "seconds")
        if res_bienes.status_code == 200:
            print("Cantidad de bienes obtenidos:", len(res_bienes.json()))
        else:
            print("Error data:", res_bienes.text)
    else:
        print("Error login data:", res_login.text)
except Exception as e:
    print("Ocurrió un error:", str(e))
