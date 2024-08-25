import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from wallet_app import config, models

if __name__ == "__main__":
    settings = config.get_settings()
    models.init_db(settings)
    asyncio.run(models.recreate_table())