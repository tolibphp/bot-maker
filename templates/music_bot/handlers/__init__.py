from .start import create_start_router
from .admin import create_admin_router
from .search import create_search_router

def get_routers(db, admin_id):
    return [
        create_start_router(db, admin_id),
        create_admin_router(db, admin_id),
        create_search_router(db, admin_id)
    ]
