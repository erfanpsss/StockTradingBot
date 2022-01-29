from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.core.management import call_command


class SiteAdmin(admin.AdminSite):
    site_header = "Stock Trading Bot"
    site_title = "Stock Trading Bot"
    index_title = "Management Panel"

    def update_site(self, request):
        call_command("update_site")
        return redirect("/admin/")


    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('update-site/', self.update_site, name="update_site"),
        ]
        return extra_urls + urls    

