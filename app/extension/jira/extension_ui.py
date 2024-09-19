from selenium.common import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue
from util.conf import JIRA_SETTINGS
from util.api.jira_clients import JiraRestClient
import random
import string

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()
create_project_option_id = 'com.epam.ework.jira.ework-integration-qa:ework-project-button_create'
issue_without_ework_project_key = 'DT-14'
issue_with_ework_project_key = 'DT-48'
ework_project_with_task = 'AUTO_STREAM'


def check_edit_project(webdriver):
    page = BasePage(webdriver)

    @print_timing("selenium_edit_project")
    def measure():
        @print_timing("selenium_edit_project:view_open_project_option")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_with_ework_project_key}")
            page.wait_until_visible((By.ID, "summary-val"))
            page.wait_until_visible((By.ID, "opsbar-operations_more")).click()
            page.wait_until_present(
                (By.ID, "com.epam.ework.jira.ework-integration-qa:ework-project-button_preview")).click()

        sub_measure()

        @print_timing("selenium_edit_project:edit_project_requirements")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//span[text()='Edit project']")).click()
            page.wait_until_visible((By.XPATH, "//input[@name='name']"))
            page.wait_until_visible((By.XPATH, "//div[text()='Instructions']")).click()
            page.wait_until_present((By.XPATH, "//trix-editor[@input='react_trix-editor_requirements']")).send_keys(
                "update")
            page.wait_until_visible((By.XPATH, "//span[text()='Save changes']")).click()
            page.wait_until_visible((By.XPATH, "//span[text()='Close Page']"))

        sub_measure()

    measure()


def check_create_project_option(webdriver):
    page = BasePage(webdriver)

    @print_timing("selenium_view_issue:view_create_project_option")
    def measure():
        page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_without_ework_project_key}")
        page.wait_until_visible((By.ID, "summary-val"))
        page.wait_until_visible((By.ID, "opsbar-operations_more")).click()
        page.wait_until_present((By.ID, create_project_option_id))

    measure()


def check_project_creation(webdriver):
    page = BasePage(webdriver)
    page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_without_ework_project_key}")

    issue_modal = Issue(webdriver)
    issue_modal.open_create_issue_modal()
    issue_modal.fill_summary_create()
    issue_modal.fill_description_create(rte_status)
    issue_modal.set_resolution()  # Set resolution if there is such field
    issue_modal.assign_to_me()
    issue_modal.submit_issue()

    page = BasePage(webdriver)

    @print_timing("selenium_create_project")
    def measure():
        @print_timing("selenium_create_project:select_project_creation_option")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//a[@class='issue-created-key issue-link']")).click()
            page.wait_until_present((By.ID, "opsbar-operations_more")).click()
            page.wait_until_visible((By.ID, create_project_option_id)).click()

        sub_measure()

        next_step = "//span[text()='Continue']"

        @print_timing("selenium_create_project:select_create_ework_project")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//div[text()='Create a Single Task']/../..")).click()
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        ework_project_name = "EWork test" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        @print_timing("selenium_create_project:fill_project_name")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//input[@name='name']")).send_keys(ework_project_name)
            page.wait_until_visible((By.XPATH, "//span[text()='Confirm and Continue']")).click()

        sub_measure()

        @print_timing("selenium_create_project:fill_project_instructions")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//trix-editor[@input='react_trix-editor_requirements']")).send_keys(
                "Test description")
            page.wait_until_visible((By.XPATH, "//input[@placeholder='Select Date']")).click()
            page.wait_until_visible((By.XPATH, "//div[contains(@class,'calendar')]"))
            page.wait_until_visible((By.XPATH, "//div[contains(@class,'sameDay')]")).click()
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:grant_access")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//input[@name='access_url']")).send_keys("https://www.google.com/")
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:configure_team")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//input[@name='use_freelancers']")).click()
            page.wait_until_visible((By.XPATH, "//div[contains(@class,'multiSelect')]")).click()
            page.wait_until_visible((By.XPATH, "//input[@name='skill_ids']/following-sibling::div/input")).send_keys(
                "AWK")
            page.wait_until_visible((By.XPATH, "//div[@title='AWK']")).click()
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:payment")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//div[@type='redactor']/input")).send_keys("40")
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        @print_timing("selenium_create_project:publish_project")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//span[text()='Publish Project']")).click()

        sub_measure()

        @print_timing("selenium_create_project:check_auto_comment")
        def sub_measure():
            actual_text = page.wait_until_visible((By.XPATH, "//div[contains(@class, 'singleTaskPreview')]/p")).text
            expected_text = "We are already looking for engineers matching your requirements. You can check the project directly in EWORK."
            assert actual_text == expected_text, f"Error: Expected '{expected_text}', but got '{actual_text}'"

        sub_measure()

    measure()


def check_task_creation(webdriver):
    page = BasePage(webdriver)
    page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_without_ework_project_key}")

    issue_modal = Issue(webdriver)
    issue_modal.open_create_issue_modal()
    issue_modal.fill_summary_create()
    issue_modal.fill_description_create(rte_status)
    issue_modal.set_resolution()  # Set resolution if there is such field
    issue_modal.assign_to_me()
    issue_modal.submit_issue()

    page = BasePage(webdriver)

    @print_timing("selenium_create_task")
    def measure():
        @print_timing("selenium_create_task:select_project_creation_option")
        def sub_measure():
            page.wait_until_present((By.XPATH, "//a[@class='issue-created-key issue-link']")).click()
            page.wait_until_present((By.ID, "opsbar-operations_more")).click()
            page.wait_until_visible((By.ID, create_project_option_id)).click()

        sub_measure()

        next_step = "//span[text()='Continue']"

        @print_timing("selenium_create_task:select_create_ework_task")
        def sub_measure():
            page.wait_until_visible(
                (By.XPATH, "//div[text()='Create a Task for an existing Stream Project']/../..")).click()
            page.wait_until_visible((By.XPATH, next_step)).click()

        sub_measure()

        ework_task_name = "EWork task" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        @print_timing("selenium_create_task:fill_task_data")
        def sub_measure():
            page.wait_until_visible((By.XPATH, "//input[contains(@class,'selected')]")).send_keys(
                ework_project_with_task)
            page.wait_until_visible((By.XPATH, "//div[contains(@type,'redactor')]")).click()
            page.wait_until_visible((By.XPATH, "//div[@type='dropdown']/div")).click()
            page.wait_until_present((By.XPATH, "//input[@name='title']")).send_keys(ework_task_name)
            page.wait_until_present((By.XPATH, "//trix-editor[@input='react_trix-editor_requirements']")).send_keys(
                "Test description")
            page.wait_until_visible((By.XPATH, "//input[@placeholder='Select Date']")).click()
            page.wait_until_visible((By.XPATH, "//div[contains(@class,'calendar')]"))
            page.wait_until_visible((By.XPATH, "//div[contains(@class,'sameDay')]")).click()
            page.wait_until_visible((By.XPATH, "//span[text()='Create Task']")).click()
            page.wait_until_visible((By.XPATH, "//h2[text()='Stream Task was published successfully']"))

        sub_measure()

    measure()
