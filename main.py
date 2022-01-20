###########
# IMPORTS #
###########

from datetime import datetime
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary  # Adds chromedriver binary to path
import json


#############
# FUNCTIONS #
#############

def on_campus(schedule):
    """
    Given a schedule string, returns if the user is on campus today or not
    
    Args:
        schedule (str): user's schedule
        FORMAT: "Schedule: [UMTWRFS]*"

    Returns:
        bool: whether user is on campus today or not
    """
    days = 'UMTWRFS'
    today_num = datetime.today().isoweekday()
    today = days[today_num]
    schedule = schedule.upper().lstrip('SCHEDULE:')
    return today in schedule


def submit_dhc(link, schedule):
    """
    Autcompletes and submits a UTD REDCAP Daily Health Check, given a user's campus schedule.

    Args:
        link (str): link to daily health check
        schedule (str): user's schedule
    """
    response = {
        'status': 0,
        'message': '',
        'stats': ''
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    web = webdriver.Chrome(options=chrome_options)
    
    try:
        web.get(link)
    except:
        response['status'] = 404
        response['message'] = 'Missing or Invalid URL.'
        return response
    
    try:
        on_campus_today = on_campus(schedule)
        
        # Fill out health check
        if on_campus_today:
            on_campus_radio_button = web.find_element(By.XPATH, '//*[@id="opt-on_campus_1"]')
            on_campus_radio_button.click()

            healthy_radio_button = web.find_element(By.XPATH, '//*[@id="id-__chk__q_1_RC_0"]')
            healthy_radio_button.click()
        else:
            not_on_campus_radio_button = web.find_element(By.XPATH, '//*[@id="opt-on_campus_0"]')
            not_on_campus_radio_button.click()

        # Submit health check
        submit_button = web.find_element(By.XPATH, '//*[@id="questiontable"]/tbody/tr[18]/td/table/tbody/tr/td/button')
        submit_button.click()
    except:
        response['status'] = 400
        response['message'] = 'Seems like this form has been filled out already or is not available.'
        return response
    
    try:
        # Check for confirmation
        web.find_element(By.XPATH, '//*[@id="surveyacknowledgment"]')
        
        # Get Daily Heath Check stats
        current_streak = web.find_element(By.XPATH, '//*[@id="pagecontent"]/div/div[3]/p[1]/strong')
        current_streak_msg = f'Current Streak: {current_streak.text}'
        
        longest_streak = web.find_element(By.XPATH, '//*[@id="pagecontent"]/div/div[3]/p[3]/strong')
        longest_streak_msg = f'Longest Streak: {longest_streak.text}'
        
        response['stats'] = '\n'.join([current_streak_msg, longest_streak_msg])
    except:
        response['status'] = 500
        response['message'] = 'Cannot confirm form submission or grab form stats. Please check confirmation of form submission.'
        return response
        
    # Return successful response
    response['status'] = 200
    response['message'] = 'Your daily health check has been successfully submitted!'
    return response


########
# MAIN #
########

app = FastAPI()

@app.get("/")
def main(link: str = '', schedule: str = ''):
    """
    Complete Daily Health Check form

    Args:
        link (str, optional): Link to REDCap. Defaults to ''.
        schedule (str, optional): Campus schedule of user. Defaults to ''.

    Returns:
        dict: response to user
    """
    if not (link or schedule):
        return {}
    
    response = submit_dhc(link, schedule)
    return response