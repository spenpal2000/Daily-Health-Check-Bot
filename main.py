from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime

def on_campus(schedule):
  # Extract schedule
  schedule = schedule.split()[1:]
  today_num = datetime.today().weekday()
  return schedule[today_num] != '*'

# Variables
link = '<insert-link-here>'
schedule = '<insert-schedule-here>'
on_campus_today = on_campus(schedule)

# USE OPTIONS FOR ONLINE IDE'S!
chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

web = webdriver.Chrome(options=chrome_options)
web.get(link)

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

# Check for confirmation
