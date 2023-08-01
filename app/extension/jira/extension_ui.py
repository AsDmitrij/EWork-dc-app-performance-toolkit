from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue
from util.conf import JIRA_SETTINGS
from util.api.jira_clients import JiraRestClient

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()
create_project_option_id = 'com.epam.ework.jira.ework-integration-qa:create-ework-project-button'


def check_create_project_option(webdriver):
    page = BasePage(webdriver)
    issue_key = 'ATES-635'

    @print_timing("selenium_view_issue:view_create_project_option")
    def measure():
        page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_key}")
        page.wait_until_visible((By.ID, "summary-val"))
        page.wait_until_present((By.ID, create_project_option_id))

    measure()


def check_project_creation(webdriver):
    issue_modal = Issue(webdriver)
    issue_modal.open_create_issue_modal()
    issue_modal.fill_summary_create()
    issue_modal.fill_description_create(rte_status)
    issue_modal.set_resolution()  # Set resolution if there is such field
    issue_modal.assign_to_me()
    issue_modal.submit_issue()

    page = BasePage(webdriver)
    last_comment = "//div[@id='issue_actions_container']//p"

    @print_timing("selenium_create_project")
    def measure():
        @print_timing("selenium_create_project:select_project_creation_option")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//a[@class='issue-created-key issue-link']")).click()
            page.wait_until_present((By.ID, "opsbar-operations_more")).click()
            page.wait_until_visible((By.ID, create_project_option_id)).click()

        sub_measure()

        next_step = "ework_next-step"

        @print_timing("selenium_create_project:fill_configure_project")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//textarea[@name='description']")).send_keys("Test description")
            page.wait_until_visible((By.ID, "ework_date-end")).click()
            page.wait_until_visible(
                (By.XPATH, "//div[@class='calendar active']//*[contains(text(),'›')]")).click()
            page.wait_until_visible((By.ID, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:grant_access")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//input[@name='access_url']")).send_keys("https://www.google.com/")
            page.wait_until_visible((By.ID, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:add_instructions")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//trix-editor[@id='ework_trix-editor']")).send_keys("Description")
            page.wait_until_visible((By.XPATH, "//aui-select[@name='task_type']")).click()
            page.wait_until_visible((By.ID, "aui-uid-0-1")).click()
            page.wait_until_visible((By.ID, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:configure_team")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//input[@name='use_freelancers']")).click()
            skills_field = "//li[@class='select2-search-field']"
            page.wait_until_visible((By.XPATH, skills_field + "/..")).click()
            page.wait_until_visible((By.XPATH, skills_field + "/input")).send_keys("COBOL")
            page.wait_until_visible((By.XPATH, skills_field + "/input")).send_keys(Keys.ENTER)
            page.wait_until_visible((By.ID, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:payment")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//aui-select[@name='story_points']")).click()
            page.wait_until_visible((By.ID, "aui-uid-3-3")).click()
            page.wait_until_visible((By.ID, "payout_per_storypoint")).send_keys("20")
            page.wait_until_visible((By.ID, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:publish_project")
        def sub_measure():
            page.wait_until_visible((By.ID, "ework_publish-project")).click()
            page.wait_until_visible((By.ID, "ework_close-page")).click()

        sub_measure()

        @print_timing("selenium_create_project:check_auto_comment")
        def sub_measure():
            actual_text = page.wait_until_visible((By.XPATH, last_comment)).text
            expected_text = "New EWORK project has been created successfully. Monitor progress directly on EWORK platform."
            assert actual_text == expected_text, f"Error: Expected '{expected_text}', but got '{actual_text}'"

        sub_measure()

    measure()

    @print_timing("selenium_check_EWork_link")
    def measure():
        page.wait_until_visible((By.XPATH, last_comment + "/a")).click()
        new_window = webdriver.window_handles[1]
        webdriver.switch_to.window(new_window)
        page.wait_until_visible((By.XPATH, "//span[text()='Sign in with your Cirro account']"))

    measure()
