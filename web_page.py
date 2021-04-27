from flask import Flask, render_template, request
from cat_data import create_breed_table
import sqlite3
# from common_fig import breed_details_fig
import os
from handle_helper import handle_breed_helper, handle_img_helper, handle_award_helper

app = Flask(__name__)






@app.route('/')
def index():
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_find_breed_name = "SELECT breed_name FROM cat_breeds"
    breed_name_list = cursor.execute(sql_find_breed_name).fetchall()
    breed_list = [x[0] for x in breed_name_list]
    connection.close()
    feature_list = ["indoor", "adaptability", "affection level", "child friendly", "dog friendly", "energy level", "health issues", "intelligence", "shedding level", "social needs", "stranger friendly", "vocalisation"]
    feature_img_list = [f"hist_{x}.png" for x in feature_list]
    return render_template('index.html', breed_list=breed_list, feature_img_list=feature_img_list)




@app.route('/handle_select')
def handle_select():
    select = request.args.get('breed')
    breed = handle_breed_helper("breed_name", select)
    img_path = breed["img_path"]

    cat_imgs = handle_img_helper(breed)
    print(len(cat_imgs))
    cat_awards = handle_award_helper(breed)
    is_result = ""
    if len(cat_awards) == 0:
        is_result = f"Sorry. No result for {breed['name']} awards!"
    return render_template('breed_detail.html', img_path=img_path, img_url_list=cat_imgs, breed=breed, award=cat_awards, is_result=is_result)


if __name__ == '__main__':
    create_breed_table()
    # breed_details_fig()
    app.run(debug=True)