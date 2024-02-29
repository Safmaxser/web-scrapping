from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import json


class WebScrapping:

    def __init__(self):
        self.browser = None
        self.parsed_data = []
        self.number_vacancies = 0
        self.select_data = {}
        self.number_selected = 0

    def _wait_element(self, delay_second=1, by=By.CLASS_NAME, value=None):
        return WebDriverWait(self.browser, delay_second).until(
            expected_conditions.presence_of_element_located((by, value)))

    def browser_chrome_init(self):
        chrome_path = ChromeDriverManager().install()
        browser_service = Service(executable_path=chrome_path)
        self.browser = Chrome(service=browser_service)

    def get_basic_data(self, url_basic):
        self.browser.get(url_basic)
        main_content = self.browser.find_element(by=By.ID,
                                                 value="a11y-main-content")
        vacancy_list = main_content.find_elements(
            by=By.CLASS_NAME, value="vacancy-serp-item-body__main-info")
        for vacancy in vacancy_list:
            try:
                title_span = vacancy.find_element(
                    by=By.CLASS_NAME, value="bloko-header-section-3")
                title_job = title_span.text
            except NoSuchElementException:
                title_job = None
            link_tag_a = vacancy.find_elements(by=By.TAG_NAME, value="a")
            link_absolute = link_tag_a[0].get_attribute("href")
            company = link_tag_a[1].text
            city_tag = vacancy.find_elements(by=By.CLASS_NAME,
                                             value="bloko-text")
            city = city_tag[1].text
            try:
                salary_tag = vacancy.find_element(
                    by=By.CLASS_NAME, value="bloko-header-section-2")
                salary_fork = salary_tag.text
            except NoSuchElementException:
                salary_fork = None
            self.number_vacancies += 1
            vacancy_dict = {
                "serial": self.number_vacancies,
                "title_job": title_job,
                "salary_fork": salary_fork,
                "company": company,
                "city": city,
                "link_absolute": link_absolute,
                "description": None
            }
            self.parsed_data.append(vacancy_dict)

    def add_description(self):
        for vacancy_dict in self.parsed_data:
            link = vacancy_dict["link_absolute"]
            self.browser.get(link)
            description_tag = self._wait_element(1, By.CLASS_NAME,
                                                 "g-user-content")
            vacancy_dict["description"] = description_tag.text.strip()

    def select_to_dict(self, search_description=None, search_salary=None):
        self.select_data = {}
        self.number_selected = 0
        for vacancy_dict in self.parsed_data:
            if (searching_values(search_description,
                                 vacancy_dict["description"]) &
                    searching_values(search_salary,
                                     vacancy_dict["salary_fork"])):
                self.number_selected += 1
                self.select_data[self.number_selected] = vacancy_dict


def searching_values(list_search, text):
    if list_search is None:
        result = True
    elif text is None:
        result = False
    else:
        result = False
        for value in list_search:
            if text.lower().find(value.lower()) != -1:
                result = True
                break
    return result


def save_file_json(path, dict_data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    web_scrapping = WebScrapping()
    web_scrapping.browser_chrome_init()

    url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
    number_pages = 2
    for page in range(number_pages):
        url_page = f'{url}&{page=}'
        web_scrapping.get_basic_data(url_page)
    print(f'Было просмотрено {web_scrapping.number_vacancies} вакансия(и/й)')
    web_scrapping.add_description()

    print()
    web_scrapping.select_to_dict(["Django", "Flask"])
    print('По условию -> в описании есть ключевые слова "Django" и "Flask"\n'
          f'Было отобрано {web_scrapping.number_selected} вакансия(и/й)')
    save_file_json("required-vacancies-description.json",
                   web_scrapping.select_data)

    print()
    web_scrapping.select_to_dict(search_salary=["$"])
    print('По условию -> вакансии только с ЗП в долларах(USD)\n'
          f'Было отобрано {web_scrapping.number_selected} вакансия(и/й)')
    save_file_json("required-vacancies-salary.json",
                   web_scrapping.select_data)
