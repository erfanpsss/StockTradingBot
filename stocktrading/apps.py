from django.contrib.admin.apps import AdminConfig

class SiteAdminConfig(AdminConfig):
    default_site = 'stocktrading.admin.SiteAdmin'