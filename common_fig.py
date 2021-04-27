import matplotlib.pyplot as plt
import matplotlib
import sqlite3
import numpy as np
import os 

def generate_all_breed_bar():
    img_dir = 'static'
    isdir = os.path.isdir(img_dir)
    if not isdir:
        os.mkdir(img_dir) 
    sql_command = "SELECT * FROM cat_breeds"
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    detail = cursor.execute(sql_command).fetchall()
    for i in detail:
        breed = {}
        breed["name"] = i[1]
        breed["id"] = i[0]
        breed["indoor"] = i[6]
        breed["temperament"] = i[2]
        breed["description"] = i[5]
        breed['adaptability'] = i[7]
        breed['affection_level'] = i[8]
        breed['child_friendly'] = i[9]
        breed['dog_friendly'] = i[10]
        breed['energy_level'] = i[11]
        breed['health_issues'] = i[12]
        breed['intelligence'] = i[13]
        breed['shedding_level'] = i[14]
        breed['social_needs'] = i[15]
        breed['stranger_friendly'] = i[16]
        breed['vocalisation'] = i[17]
        breed['wiki'] = i[18]
        img_file_name = f"static/{breed['name'].lower().replace(' ','_')}.png"
        isfile = os.path.isfile(img_file_name)
        if not isfile:
            breed_details_fig(breed)




def breed_details_fig(breed):
    file_name = f"static/{breed['name'].lower().replace(' ','_')}.png"
    is_file = os.path.isfile(file_name)
    if not is_file:
        fig = plt.figure(figsize = (12,10))
        xs = ["indoor", "adaptability", "affection_level", "child_friendly", "dog_friendly", "energy_level", "health_issues", "intelligence", "shedding_level", "social_needs", "stranger_friendly", "vocalisation"]

        ys = [breed["indoor"], breed["adaptability"], breed["affection_level"], breed["child_friendly"], breed["dog_friendly"], breed["energy_level"], breed["health_issues"], breed["intelligence"], breed["shedding_level"], breed["social_needs"], breed["stranger_friendly"], breed["vocalisation"]]
        ys_fig = [float(x) for x in ys]
        plt.bar(np.arange(len(xs)),ys_fig)
        plt.xticks(np.arange(len(xs)), xs, rotation = 45)
        fig.savefig(file_name)
        plt.close()


def breeds_origin_distribution():
    is_file = os.path.isfile("static/origin_pie.png")
    if not is_file:
        connection = sqlite3.connect("cache.db")
        cursor = connection.cursor()
        sql_command = f"SELECT * FROM cat_breeds"
        cat_breeds = cursor.execute(sql_command).fetchall()
        connection.close()
        origin_code = [x[4] for x in cat_breeds]
        unique_code = set(origin_code)
        unique_code = list(unique_code)
        num = [origin_code.count(x)/len(origin_code)*100 for x in unique_code]
        plt.pie(num, labels=unique_code)
        plt.savefig("static/origin_pie.png") 
        plt.close()


def feature_his():
    feature_list = ["indoor", "adaptability", "affection level", "child friendly", "dog friendly", "energy level", "health issues", "intelligence", "shedding level", "social needs", "stranger friendly", "vocalisation"]
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_command = f"SELECT * FROM cat_breeds"
    all_data = cursor.execute(sql_command).fetchall()
    connection.close()
    indoor = [i[6] for i in all_data]
    adaptability = [i[7] for i in all_data]
    affection_level = [i[8] for i in all_data]
    child_friendly = [i[9] for i in all_data]
    dog_friendly = [i[10] for i in all_data]
    energy_level = [i[11] for i in all_data]
    health_issues = [i[12] for i in all_data]
    intelligence = [i[13] for i in all_data]
    shedding_level = [i[14] for i in all_data]
    social_needs = [i[15] for i in all_data]
    stranger_friendly = [i[16] for i in all_data]
    vocalisation = [i[17] for i in all_data]
    
    feature_data_list = [indoor, adaptability, affection_level, child_friendly, dog_friendly, energy_level, health_issues, intelligence, shedding_level, social_needs, stranger_friendly, vocalisation]
    for i in feature_data_list:
        idx = feature_data_list.index(i)
        file_name = f"static/hist_{feature_list[idx]}.png"
        if not os.path.isfile(file_name):
            fig = plt.figure(figsize = (8,6))
            plt.hist(i, bins=5)
            plt.xlabel("Scores")  
            plt.ylabel("Number of breeds")
            plt.title(f"Histogram for {feature_list[idx]} ")
            plt.savefig(file_name) 
            plt.close()


if __name__ == "__main__":
    generate_all_breed_bar()
    breeds_origin_distribution()
    feature_his()