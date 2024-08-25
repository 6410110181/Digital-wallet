from . import items
from . import merchants
from . import transactions
from . import wallets
from . import buy_items

from . import users

from . import authentication

def init_router(app):
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(transactions.router)
    app.include_router(wallets.router)
    app.include_router(buy_items.router)