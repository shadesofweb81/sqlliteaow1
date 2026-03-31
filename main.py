"""
Accounting ERP – Offline-first desktop application.
SQLite local database with cloud PostgreSQL sync.
"""

from Database.db_manager import DatabaseManager
from Services.session import Session
from Services.async_runner import AsyncRunner


def main():
    # Start the background asyncio event loop
    AsyncRunner.start()

    # Initialize local SQLite database (creates tables if needed)
    db = DatabaseManager()
    db.initialize_database()

    # If a saved session exists skip the login screen, otherwise show login
    if Session.load() and Session.is_logged_in():
        _launch_app()
    else:
        from Forms.auth.login_form import LoginForm
        LoginForm(on_success=_launch_app).run()


def _launch_app():
    """Pull user companies, pick one, then open the main dashboard."""
    from Services.pull_service import PullService
    from Services.async_runner import AsyncRunner

    # Pull user companies from cloud first (blocking, quick operation)
    try:
        future = AsyncRunner.run(PullService.pull_all())
        future.result(timeout=10)
    except Exception:
        pass  # Whether pull succeeded or not, proceed to company selection

    _show_company_selector()


def _show_company_selector():
    """Show the select-company dialog, then open MainForm."""
    from Forms.company.select_company_form import SelectCompanyForm

    def _on_company_selected(company):
        from Forms.main_form import MainForm
        MainForm().run()

    SelectCompanyForm(on_select=_on_company_selected).run()


if __name__ == "__main__":
    main()
