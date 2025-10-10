import argparse
import random
import string
import requests

def main():
    # Configurazione del parser per i parametri
    parser = argparse.ArgumentParser(description='Script per richieste GET infinite')
    parser.add_argument('-S', '--seed', type=int, default=None, help='Valore del seed per l\'invariazione random')
    parser.add_argument('-p', '--port', type=int, required=True, help='Porta da utilizzare nell\'URL')
    args = parser.parse_args()

    # Imposta il seed per la generazione random
    if args.seed:
        random.seed(args.seed)

    # Genera una stringa casuale di 4 byte
    chars = ''.join(random.choice(string.hexdigits) for _ in range(8))
    
    # URL target (modifica come necessario)
    url = f'http://127.0.0.1:{args.port}'

    # Header da inviare
    headers = {
        'X-Random-String': chars,
        'User-Agent': 'PythonScriptGenerator/1.0'
    }

    # Loop infinito per le richieste
    while True:
        try:
            print(f'Effettuo richiesta a: {url}')
            response = requests.get(url, headers=headers, timeout=2)
            print(f'Risposta ricevuta con status code: {response.content}')
        except Exception as e:
            print(f'Errore durante la richiesta: {e}')
        # puoi aggiungere un timeout qui se necessario
        # time.sleep(1)  # per esempio

if __name__ == '__main__':
    main()