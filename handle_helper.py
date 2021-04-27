from flask import Flask, render_template, request
from cat_data import get_breed_img, get_award_breed
import sqlite3
from common_fig import breed_details_fig
import os




def handle_breed_helper(id_or_name, breed_id_name):
    breed = {}
    sql_command = f"SELECT * FROM cat_breeds WHERE {id_or_name}='{breed_id_name}'"
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    detail = cursor.execute(sql_command).fetchall()
    breed["name"] = detail[0][1]
    breed["id"] = detail[0][0]
    breed["indoor"] = detail[0][6]
    breed["temperament"] = detail[0][2]
    breed["description"] = detail[0][5]
    breed['adaptability'] = detail[0][7]
    breed['affection_level'] = detail[0][8]
    breed['child_friendly'] = detail[0][9]
    breed['dog_friendly'] = detail[0][10]
    breed['energy_level'] = detail[0][11]
    breed['health_issues'] = detail[0][12]
    breed['intelligence'] = detail[0][13]
    breed['shedding_level'] = detail[0][14]
    breed['social_needs'] = detail[0][15]
    breed['stranger_friendly'] = detail[0][16]
    breed['vocalisation'] = detail[0][17]
    breed['wiki'] = detail[0][18]
    breed["img_path"] = f"{breed['name'].lower().replace(' ','_')}.png"
    connection.close()
    return breed

def handle_img_helper(breed):
    get_breed_img(breed)
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_command = f"SELECT * FROM cat_images WHERE breed_id='{breed['id']}'"
    cat_imgs = cursor.execute(sql_command).fetchall()
    cat_img_urls = []
    connection.close()
    for i in cat_imgs:
        an_img = {}
        an_img["url"] = i[2]
        an_img["height"] = i[-1]
        an_img["width"] = i[-2]
        ratio = an_img["height"] / an_img["width"]
        an_img["height"] = 200 * ratio
        an_img["width"] = 200
        cat_img_urls.append(an_img)
    print(len(cat_img_urls))
    return cat_img_urls

def handle_award_helper(breed):
    get_award_breed(breed)
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_command = f"SELECT * FROM cat_awards WHERE breed_id='{breed['id']}'"
    cat_award_list = cursor.execute(sql_command).fetchall()
    connection.close()
    cat_award_list_clean=[]
    for i in cat_award_list:
        cat = {}
        cat["name"] = i[1]
        cat["img_url"] = i[2]
        cat["season"] = i[4]
        cat["award"] = i[5]
        cat["info"] = i[6]
        cat_award_list_clean.append(cat)
    return cat_award_list_clean