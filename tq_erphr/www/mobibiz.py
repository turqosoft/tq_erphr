import frappe
from tq_erphr.pwa_api import get_boot

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context = frappe._dict()
	context.csrf_token = csrf_token
	context.boot = get_boot()
	context.site_name = frappe.local.site
	context.title = "MobiBiz Lite"
	context.app_name = "MobiBiz Lite"
	return context
