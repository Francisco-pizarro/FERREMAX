import random
from transbank.webpay.webpay_plus.transaction import Transaction

def iniciar_transaccion(return_url):
    buy_order = str(random.randrange(1000000, 99999999))
    session_id = str(random.randrange(1000000, 99999999))
    amount = random.randrange(10000, 1000000)

    tx = Transaction()
    response = tx.create(buy_order, session_id, amount, return_url)
    return response['url'], response['token']

def confirmar_transaccion(token_ws):
    tx = Transaction()
    response = tx.commit(token_ws)
    return response