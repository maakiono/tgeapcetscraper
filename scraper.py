from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import pandas as pd
import os

clg_dropdown_list_options = []
branch_dropdown_list_options = []
driver = webdriver.Firefox()
driver.get("https://tgeapcet.nic.in")

while driver.current_url != "https://tgeapcet.nic.in/default.aspx":
    sleep(2)
while True:
    try:
        clg_allotment_hplink = driver.find_element(By.LINK_TEXT, "College-wise Allotment Details")
        clg_allotment_hplink.click()
        break
    except:
        continue
sleep(1)
driver.switch_to.window(driver.window_handles[1])
while len(clg_dropdown_list_options) <= 0:
    sleep(2)
    clg_dropdown_list = driver.find_element(By.ID,"MainContent_DropDownList1")
    clg_dropdown_list_options = [college.text for college in clg_dropdown_list.find_elements(By.TAG_NAME, "option")]
print("Site Setup Finished, Starting now.")

if not os.path.exists("cache"):
    os.makedirs("cache")
    
for college in reversed(clg_dropdown_list_options):
    while True:
        try:
            clg_dropdown_list = driver.find_element(By.ID,"MainContent_DropDownList1")
            clg_sel = Select(clg_dropdown_list)
            clg_sel.select_by_visible_text(college)
            branch_dropdown_list_options = []
            print("Selected College:",college)
            break
        except:
            sleep(.5)
            continue
    while len(branch_dropdown_list_options) <= 0:
        branch_dropdown_list = driver.find_element(By.ID,"MainContent_DropDownList2")
        branch_dropdown_list_options = [branch.text for branch in branch_dropdown_list.find_elements(By.TAG_NAME, "option")]
        sleep(1)
    for branch in branch_dropdown_list_options:
        if branch == "--Select Branch--":
            continue
        if os.path.exists('cache/'+college+"::"+branch+".csv"):
            print("Cache Hit, Skipping ⚠️")
            continue
        while True:
            try:
                branch_dropdown_list = driver.find_element(By.ID,"MainContent_DropDownList2")
                branch_sel = Select(branch_dropdown_list)
                branch_sel.select_by_visible_text(branch)
                print("Processing College:",college,"| Branch:",branch)
                break
            except:
                clg_dropdown_list = driver.find_element(By.ID,"MainContent_DropDownList1")
                clg_sel = Select(clg_dropdown_list)
                clg_sel.select_by_visible_text(college)
                print("Reelected College to escape error:",college)
                sleep(.5)
                continue
        show_allot = driver.find_element(By.ID,"MainContent_btn_allot")
        show_allot.click()
        sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            table = soup.find_all("table")[-1]
        except IndexError:
            print("No Seats Allocated in College or Errored out")
            driver.find_element(By.XPATH,"/html/body/right/a/img").click()
            continue
        rows = [[cell.text.strip() for cell in row.find_all("td")] for row in table.find_all("tr")]
        _ = pd.DataFrame(rows)
        del _[0]
        _.columns = ["Hall Ticket No","Rank","Name of the Candidate","Sex","Caste","Region","Seat Category"]
        _["Branch"] = branch
        _["College"] = college
        _.to_csv(f"cache/{college}::{branch.replace("/","|")}.csv")
        del _
        print("Done Processing College:",college,"| Branch:",branch,"✨")
print("Done scraping, Building final result")
result = pd.DataFrame()
for dat in os.listdir("cache"):
    newdat = pd.read_csv("cache/"+dat.replace("/","|"),index_col=0)
    result = pd.concat([result,newdat],ignore_index=True)
    del newdat
    os.remove("cache/"+dat.replace("/","|"))
result.to_csv("result.csv")
os.rmdir("cache")
print("Done")
driver.quit()