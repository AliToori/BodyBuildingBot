#!/usr/bin/env python3
import os
import re
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class ScraperX:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument('--headless')

    def __init__(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.is_signed_in = False
        self.is_country_selected = False
        self.is_first_upload = True

    def get_products(self, url, product_category, num_of_product):
        self.driver.get(url + product_category)
        sleep(3)
        if not self.is_country_selected:
            self.driver.find_element_by_class_name('Modal-inner').find_element_by_tag_name('button').click()
            sleep(5)
            self.is_country_selected = True
        actions = ActionChains(self.driver)
        for i in range(0, num_of_product, 20):
            product_links = {product_category: [product.get_attribute('href') for product in
                                              self.driver.find_elements_by_class_name('product__name')[i:]]}
            df = pd.DataFrame.from_dict(product_links)
            # if file does not exist write header
            if not os.path.isfile(product_category + 'links.csv'):
                df.to_csv(product_category + 'links.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + 'links.csv', mode='a', header=False, index=None)
            load_more_button = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="js-bbcom-app"]/div/div/div/div[2]/section/a/span[1]')))
            actions.move_to_element(load_more_button)
            actions.click(load_more_button)
            actions.perform()
            sleep(3)

        df = pd.read_csv(product_category + "links.csv", index_col=None)
        for index, row in df.iterrows():
            product = {}
            self.driver.get(url=row[product_category])
            sleep(3)
            product_name = self.driver.find_element_by_class_name('Product__name').text
            price = self.driver.find_element_by_class_name('sku-chooser__sale-price ').text
            price = price[1:]
            price_per_serving = self.driver.find_element_by_class_name('sku-chooser__price-per').text
            price_per_serving = price_per_serving[2:6]
            table_text = self.driver.find_element_by_tag_name('tbody').text
            print("Table text: ", table_text)
            protein_content = re.findall(r'(?<=Protein |protein )(\d.+)g', table_text)
            if len(protein_content) > 0:
                protein_content = protein_content[0]
            calories = re.findall(r'(?<=Calories )(\d{1,5})', table_text)
            if len(calories) > 0:
                calories = calories[0]
            else: calories = 0
            serving_size = re.findall(r'(?<=Scoop \()(.*)g|(?<=Bar \()(.*)g', table_text)
            if len(serving_size) > 0:
                serving_size = re.sub(r'\D', '', str(serving_size))
            else: serving_size = 0
            servings_per_container = re.findall(r'(?<=about )(\d{1,3})|(?<=Servings Per Container)(\d{1,3})|(?<=Servings Per Container:)(\d{1,3})', table_text)
            if len(servings_per_container) > 0:
                servings_per_container = re.sub(r'\D', '', str(servings_per_container))
            else: servings_per_container = 0
            fat_content = re.findall(r'(?<=Total Fat )(.*)g', table_text)
            if len(fat_content) > 0:
                fat_content = fat_content[0]
            else: fat_content = 0
            sugar = re.findall(r'(?<=Sugars )|(?<=Sugars \(less than\) )(\d)', table_text)
            if len(sugar) > 0 and str(sugar).lower() != 'nan':
                sugar = sugar[0]
            else: sugar = 0
            vegan = re.findall(r'(?<=Vegan )', table_text)
            if len(vegan) > 0:
                vegan = 'Yes'
            else: vegan = 'No'
            product["product_name"] = [product_name]
            product["buy_link"] = [row[product_category]]
            product["protein_content"] = [protein_content]
            product["fat_content"] = [fat_content]
            product["calories"] = [calories]
            product["serving_size"] = [serving_size]
            product["price"] = [price]
            product["servings"] = [servings_per_container]
            product["price_per_serving"] = [price_per_serving]
            product["vegan"] = [vegan]
            product["sugar"] = [sugar]
            df = pd.DataFrame.from_dict(product)
            # if file does not exist write header
            if not os.path.isfile(product_category + '.csv'):
                df.to_csv(product_category + '.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + '.csv', mode='a', header=False, index=None)

    def get_preworkout(self, url, product_category, num_of_products):
        self.driver.get(url + product_category)
        sleep(3)
        if not self.is_country_selected:
            self.driver.find_element_by_class_name('Modal-inner').find_element_by_tag_name('button').click()
            self.is_country_selected = True
        for i in range(0, num_of_products, 20):
            product_links = {product_category: [product.get_attribute('href') for product in
                                              self.driver.find_elements_by_class_name('product__name')[i:]]}
            df = pd.DataFrame.from_dict(product_links)
            # if file does not exist write header
            if not os.path.isfile(product_category + 'links.csv'):
                df.to_csv(product_category + 'links.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + 'links.csv', mode='a', header=False, index=None)
            load_more_button = self.driver.find_element_by_class_name('lazy-loader')
            self.driver.execute_script('arguments[0].scrollIntoView(true);', load_more_button)
            self.driver.find_element_by_class_name('lazy-loader').click()
            sleep(3)

        df = pd.read_csv(product_category + "links.csv", index_col=None)
        for index, row in df.iterrows():
            product = {}
            self.driver.get(url=row[product_category])
            sleep(3)
            product_name = self.driver.find_element_by_class_name('Product__name').text
            table_text = self.driver.find_element_by_class_name('facts_table').text
            citrulline_malate = re.findall(r'(?<=Citrulline Malate	)(.*)g', table_text)
            if len(citrulline_malate) > 0:
                citrulline_malate = citrulline_malate[0]
            else: citrulline_malate = 0
            beta_alanine = re.findall(r'(?<=Beta-Alanine)(.*)mg|(?<=Beta-Alanine \(as CarnoSyn®\).)(\d)', table_text)
            if len(beta_alanine) > 0:
                beta_alanine = beta_alanine[0]
            else: beta_alanine = 0
            creatine = re.findall(r'(?<=Creatine Nitrate \(NO3-T®\)	)(.*)g|(?<=Creatine HCl \(as CON-CRET®\)	)(.*)g', table_text)
            if len(creatine) > 0:
                creatine = creatine[0]
            else: creatine = 0
            caffeine = re.findall(r'(?<=Caffeine Anhydrous \()(.*)mg|(?<=Natural Caffeine \(from Coffee Bean\))(.*)mg', table_text)
            if len(caffeine) > 0:
                caffeine = caffeine[0]
            else: caffeine = 0
            taurine = re.findall(r'(?<=Taurine	)(.*)g', table_text)
            if len(taurine) > 0:
                taurine = taurine[0]
            else: taurine = 0
            agmatine_sulfate = re.findall(r'(?<=Agmatine Sulfate )(\d)mg', table_text)
            if len(agmatine_sulfate) > 0:
                agmatine_sulfate = agmatine_sulfate[0]
            else: agmatine_sulfate = 0
            arginine = re.findall(r'(?<=Arginine Silicate)(.*\d)g|(?<=Arginine Alpha Ketoglutarate	)(\d*)g', table_text)
            if len(arginine) > 0:
                arginine = arginine[0]
            else: arginine = 0
            betaine = re.findall(r'(?<=Betaine Nitrate \(as NO3-T®\))(.*)mg|(?<=Betaine \(Trimethylglycine\).)(\d.\d)|(?<=Betaine Anhydrous)(.*)mg', table_text)
            if len(betaine) > 0:
                betaine = betaine[0]
            else: proprietary_blend = 0
            proprietary_blend = re.findall(r'(Proprietary Blend)', table_text)
            if len(proprietary_blend) > 0:
                proprietary_blend = 'Yes'
            else: proprietary_blend = 'No'
            product["product_name"] = [product_name]
            product["buy_link"] = [row[product_category]]
            product["citrulline_malate"] = [citrulline_malate]
            product["beta_alanine"] = [beta_alanine]
            product["creatine"] = [creatine]
            product["caffeine"] = [caffeine]
            product["taurine"] = [taurine]
            product["agmatine_sulfate"] = [agmatine_sulfate]
            product["arginine"] = [arginine]
            product["betaine"] = [betaine]
            product["proprietary_blend"] = [proprietary_blend]
            print("Product:", product)
            df = pd.DataFrame.from_dict(product)
            # if file does not exist write header
            if not os.path.isfile(product_category + '.csv'):
                df.to_csv(product_category + '.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + '.csv', mode='a', header=False, index=None)

    def upload_products(self, url, product_category):
        self.driver.get(url=url)
        sleep(3)
        if not self.is_signed_in:
            self.driver.find_element_by_id('user_login').send_keys('admin')
            self.driver.find_element_by_id('user_pass').send_keys('Demo@12345!!!')
            self.driver.find_element_by_id('rememberme').click()
            self.driver.find_element_by_id('wp-submit').click()
            sleep(5)
            self.is_signed_in = True
        df = pd.read_csv(product_category + ".csv", index_col=None)
        for index, row in df.iterrows():
            # self.driver.get(url=url)
            sleep(1)
            print("Uploading Product: ", index, row['product_name'], row['buy_link'])
            title = self.driver.find_element_by_id('title')
            title.clear()
            title.send_keys(row['product_name'])
            if not self.is_first_upload:
                print('check1')
                self.driver.find_element_by_id('edit-slug-buttons').find_element_by_tag_name('button').click()
                new_slug = self.driver.find_element_by_id('new-post-slug')
                new_slug.clear()
                new_slug.send_keys(row['product_name'])
                self.driver.find_element_by_id('edit-slug-buttons').find_element_by_tag_name('button').click()
            if product_category == 'protein':
                self.driver.find_element_by_id('in-c_categories-3').click()
            elif product_category == 'preworkout':
                self.driver.find_element_by_id('in-c_categories-5').click()
            else:
                self.driver.find_element_by_id('in-c_categories-4').click()
            buy = self.driver.find_element_by_id('buy-link')
            buy.clear()
            buy.send_keys(str(row['buy_link']))
            protein_content = self.driver.find_element_by_id('protein-content-g')
            protein_content.clear()
            protein_content.send_keys(str(row['protein_content']))
            fat_content = self.driver.find_element_by_id('fat-content-g')
            fat_content.clear()
            fat_content.send_keys(str(row['fat_content']))
            calories = self.driver.find_element_by_id('calories')
            calories.clear()
            calories.send_keys(str(row['calories']))
            serving_size = self.driver.find_element_by_id('serving-size-g')
            serving_size.clear()
            serving_size.send_keys(str(row['serving_size']))
            price = self.driver.find_element_by_id('price-usd')
            price.clear()
            price.send_keys(str(row['price']))
            servings = self.driver.find_element_by_id('servings')
            servings.clear()
            servings.send_keys(str(row['servings']))
            price_per_serving = self.driver.find_element_by_id('price-serving-g')
            price_per_serving.clear()
            price_per_serving.send_keys(str(row['price_per_serving']))
            Select(self.driver.find_element_by_id('vegan')).select_by_visible_text(str(row['vegan']))
            sugar = self.driver.find_element_by_id('sugar-g')
            sugar.clear()
            sugar.send_keys(str(row['sugar']))
            button_publish = self.driver.find_element_by_id('publish')
            actions = ActionChains(self.driver)
            actions.move_to_element(button_publish)
            sleep(1)
            actions.click(button_publish)
            actions.perform()
            self.is_first_upload = False
            sleep(3)
            print('Product Successfully Uploaded: ', index, row['product_name'], row['buy_link'])
            # self.driver.find_element_by_class_name('page-title-action').click()

    def finish(self):
        self.driver.close()
        self.driver.quit()


def main():
    # ***************************************************************
    #    The program starts from here
    # ***************************************************************
    upload_url = 'http://suppviz.com/wp-admin/post-new.php?post_type=supplements'
    main_url = 'https://www.bodybuilding.com/'
    protein = "protein"
    preworkout = "preworkout"
    scraperx = ScraperX()
    num_of_products = 100
    # scraperx.get_products(url=main_url, product_category=protein, num_of_product=num_of_products)
    # scraperx.get_products(url=main_url, product_category=preworkout, num_of_product=num_of_products)
    scraperx.upload_products(url=upload_url, product_category=protein)
    scraperx.upload_products(url=upload_url, product_category=preworkout)
    scraperx.finish()


if __name__ == '__main__':
    main()