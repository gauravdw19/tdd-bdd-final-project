import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ID_PREFIX = "product_"

# Fallback wait time
WAIT_SECONDS = 10

##################################################################
# NAVIGATION
##################################################################

@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        lambda d: message in d.title
    )


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert text_string not in element.text


##################################################################
# BUTTON CLICK
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + "-btn"
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, button_id))
    )
    element.click()


##################################################################
# VERIFY TEXT IN RESULTS
##################################################################

@then('I should see "{name}" in the results')
def step_impl(context, name):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        lambda driver: name in driver.find_element(By.ID, "search_results").text
    )


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        lambda driver: name not in driver.find_element(By.ID, "search_results").text
    )


##################################################################
# FLASH MESSAGE
##################################################################

@then('I should see the message "{message}"')
def step_impl(context, message):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.text_to_be_present_in_element((By.ID, "flash_message"), message)
    )


##################################################################
# FIELD INPUT
##################################################################

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.text_to_be_present_in_element_value((By.ID, element_id), text_string)
    )


##################################################################
# DROPDOWNS
##################################################################

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    dropdown = Select(
        WebDriverWait(context.driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    )
    dropdown.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    dropdown = Select(context.driver.find_element(By.ID, element_id))
    assert dropdown.first_selected_option.text == text


##################################################################
# COPY / PASTE
##################################################################

@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)