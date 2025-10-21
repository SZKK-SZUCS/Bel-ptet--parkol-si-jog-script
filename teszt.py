from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
import csv
import time
from datetime import datetime
import os
import secrets
import json
from dataclasses import dataclass
from typing import List

# Define driver
driver = webdriver.Chrome()
driver.maximize_window() #Teljes képernyőssé teszi az ablakot

# Define WebDriverWait instance
wait = WebDriverWait(driver, 10)
waitForError = WebDriverWait(driver, 1)

oldal =  "https://beleptetoadmin.sze.hu/"
##TODO: ADD MEG!
username = ""
password = ""

# JSON fileból be olvassuk a recordokat

@dataclass
class PersonRecord:
    kartya: str
    permissions: List[str]
    plates: List[str]

def load_records(path: str) -> List[PersonRecord]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    records = []
    for rec in raw:
        kartya = rec.get("kartya", "")
        permissions = [val for key, val in rec.items()
                       if key.startswith("jog") and val]
        plates = [val for key, val in rec.items()
                  if key.lower().startswith("rendszam") and val]
        records.append(PersonRecord(kartya, permissions, plates))
    return records

#TODO: add meg a JSON path-et a relative path kimásolásával
persons = load_records("")

# Jogosultság lejárat
date_target = "2026-10-01"

#Logolás egy csv fájlba:
#Ahányszor lefutatod a programot egy csv fájl keletkezik a logs mappában
TOP_LEVEL_LOGS = "logs"

def new_log_path(prefix="permission_checks", ext="csv"):
    # Ensure top-level logs folder exists
    os.makedirs(TOP_LEVEL_LOGS, exist_ok=True)
    # Create/bucket by day
    day_folder = datetime.now().strftime("%Y-%m-%d")
    day_path = os.path.join(TOP_LEVEL_LOGS, day_folder)
    os.makedirs(day_path, exist_ok=True)
    # Timestamped filename for each run
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Optional short random suffix to avoid collisions on rapid restarts
    suffix = secrets.token_hex(2)
    filename = f"{prefix}_{ts}_{suffix}.{ext}"
    return os.path.join(day_path, filename)

LOG_FILE = new_log_path()

with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "card_num", "action", "result"])

def log_action(card_num, action, result):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(sep=" ", timespec="seconds"),
            card_num,
            action,
            result
        ])

def login() :
        driver.get(oldal) #Betölti az oldalt
        time.sleep(0.5)
        main = driver.current_window_handle # kijelöli a beleptetőt a jelenlegi ablaknak
        login_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[.//span[contains(normalize-space(.), 'Bejelentkezés címtárral')]]"
    ))) #Bejelentkezés gomb kiválasztása
        login_btn.click() #Bejelentkezés gomb megnyomása
        wait.until(lambda d: len(d.window_handles) == 2) #Második ablak keresése/megvárása
        for h in driver.window_handles:
            if h != main:
                driver.switch_to.window(h) #Második ablakra átváltás
                break
        time.sleep(1)
        #felhasználónév és jelszó bemásolása
        login_username_el = wait.until(EC.element_to_be_clickable((By.ID,"username")))
        login_username_el.send_keys(username)
        login_password_el = wait.until(EC.element_to_be_clickable((By.ID,"password")))
        login_password_el.send_keys(password)
        login_btn_el = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"loginbutton")))
        login_btn_el.click()
        # vissza váltás a fő oldalra
        driver.switch_to.window(main)

def navigation() :
    driver.get("https://beleptetoadmin.sze.hu/cards/list")

#Amikor oldalon belül le kell görgetni, ezt a funkciót kell használni
def scroll(element) :
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'nearest'});", element)
    driver.execute_script("window.scrollBy(0, -100);")
    time.sleep(0.2)

def find_kartya(person) :
    time.sleep(3) # Ezt kell módosítani, ha szar a neted és kicrashelsz a kártya keresésnél
    kartya = person.kartya
    #Végig iterál a megadott kártyákon és lefutattja a jog csekkoló/beállító funkciót
    card_number_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Kártyaszám']/following::input[1]")))
    card_number_box.clear() 
    card_number_box.send_keys(kartya)
    try:

        err = waitForError.until(EC.visibility_of_element_located((By.XPATH, "//td[@colspan='7' and normalize-space(.)='Nincs elérhető adat']")))
        # Found error element
        log_action(kartya, "Card Error", "Card doesn't exist❗")
    except TimeoutException:
        # No error element within timeout
            print()
            edit_btn = wait.until(EC.element_to_be_clickable((By.XPATH,"//td[contains(@class,'text-end')]/a[.//i[contains(@class,'mdi-pencil')]]")))
            edit_btn.click()
            print("Szerkesztés gomb megnyomva")
            edit_permissions(person)
            edit_license_plate(person)

#elötte mindig scrolloljunk a megfelelő naptár inputhoz
def calendar_handler():
    month_btn = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[normalize-space(text())='2025. október']")))
    month_btn.click()
    #
    next_year = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Következő év']")))
    next_year.click()
    time.sleep(1) #kell idő rerenderelni
    #
    oktober_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//td/button[.//div[@class='v-btn__content' and normalize-space(.)='okt.']]")))
    oktober_btn.click()
    time.sleep(1) #kell idő rerenderelni
    #
    first_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//td/button[.//div[@class='v-btn__content' and normalize-space(.)='1']]")))
    first_btn.click()

def edit_permissions(person) :
    wrapper = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".v-data-table__wrapper"))) #Jogok táblázat kikeresése
    time.sleep(1)
    rows = wrapper.find_elements(By.CSS_SELECTOR, "tbody > tr") #Táblában található sorok kikeresése

    permission_targets = person.permissions
    kartya = person.kartya

    #Végig iterálunk a jogokon, majd jogonként a sorokon
    for permission_target in permission_targets:
        permission_match = False
        for row in rows:
            scroll(row)
            permission_input = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) .v-select__slot input[type='text']")
            permission_value = permission_input.get_attribute("value") or permission_input.get_attribute("placeholder")

            #Ha megvan a keresett jog akkor igazra állítjuk a match változót és tovább megyünk a dátum ellenőrzésre
            if (permission_value == permission_target) :
                permission_match = True
                date_input = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) input[type='text']")
                date_value = date_input.get_attribute("value") or date_input.get_attribute("placeholder")
                if (date_value == date_target) :
                    #Ha a dátum is jó akkor logoljuk és kilépünk a sor iterációból
                    log_action(kartya, f"Checked {permission_target} permission", "Everything was correct ✅")
                    break
                #Ha nem jó a dátum akkor beállítjuk
                else:
                    scroll(date_input)
                    date_input.click()
                    #
                    calendar_handler()
                    #
                    save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Mentés']")))
                    scroll(save_btn)
                    save_btn.click()
                    log_action(kartya, f"Checked {permission_target} permission", "Permission was correct, Date corrected 🔧✅")
                    break

        #Ha egyik sorba se találtuk meg a jogot akkor beállítjuk
        if permission_match == False :
                add_permission_btn = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[.//i[contains(@class,'mdi-plus')] and contains(normalize-space(.), 'Hozzáadás')]")))
                scroll(add_permission_btn)
                add_permission_btn.click()
                #Újra töltöm a sorok arrayt és kiválasztom az utolsó sort
                rows = wrapper.find_elements(By.CSS_SELECTOR, "tbody > tr")
                last_row = rows[-1]
                #inputok megkeresése
                permission_input = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(1) .v-select__slot input[type='text']")
                date_input = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(2) input[type='text']")
                #inputokba az adatok feltöltése
                permission_input.click()
                permission_input.send_keys(permission_target)
                option = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@role='option' and .//span[normalize-space(text())='"+permission_target+"']]"
                )))
                option.click()
                scroll(date_input)
                date_input.click()
                #
                calendar_handler()
                #
                save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Mentés']")))
                scroll(save_btn)
                save_btn.click()
                log_action(kartya, "Checked permissions", f"{permission_target} permission and Date added 🛠️✅")

def edit_license_plate(person) :
    parkolas_tab = wait.until(EC.element_to_be_clickable((
    By.XPATH,
    "//div[@role='tab' and normalize-space(text())='Parkolás']"
)))
    scroll(parkolas_tab)
    parkolas_tab.click()

    title = wait.until(EC.presence_of_element_located((
    By.XPATH,
    "//div[contains(@class,'v-card__title') and normalize-space(text())='Rendszámok']"
)))
    wrapper = title.find_element(
    By.XPATH,
    "following-sibling::div//div[contains(@class,'v-data-table__wrapper')]"
)
    time.sleep(1)
    rows = wrapper.find_elements(By.CSS_SELECTOR, "tbody > tr") #Táblában található sorok kikeresése

    license_plate_numbers = person.plates
    kartya = person.kartya

    for license_plate in license_plate_numbers:
        license_plate_match = False
        for row in rows:
            scroll(row)
            license_plate_input = row.find_element(By.CSS_SELECTOR,"td:nth-child(2) input[type='text']")
            license_plate_value = license_plate_input.get_attribute("value") or license_plate_input.get_attribute("placeholder")
            #Ha megvan a keresett rendszám akkor tovább lépünk
            if (license_plate_value == license_plate) :
                license_plate_match = True
                log_action(kartya, "Checked License Plate", "Found ✅")
                break
            #Ha nincs meg akkor hozzáadjuk
        if (license_plate_match == False) :
            add_permission_btn = title.find_element(By.XPATH,"following-sibling::div//button[.//i[contains(@class,'mdi-plus')] and contains(normalize-space(.), 'Hozzáadás')]")
            scroll(add_permission_btn)
            add_permission_btn.click()
            #Újra töltöm a sorok arrayt és kiválasztom az utolsó sort
            rows = wrapper.find_elements(By.CSS_SELECTOR, "tbody > tr")
            last_row = rows[-1]
            #inputok megkeresése
            license_plate_input = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(2) input[type='text']")
            license_plate_input.click()
            license_plate_input.send_keys(license_plate)
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Mentés']")))
            scroll(save_btn)
            save_btn.click()
            log_action(kartya, "Checked License Plate", f"Added {license_plate} 🛠️✅")

try:
    login ()
    for person in persons:
        navigation()
        find_kartya(person)
        time.sleep(0.5)
    time.sleep(5)
    driver.quit()
except WebDriverException as e:
    log_action(0, "Driver Error", f"Could not load page: {oldal} - {e} ❗")
