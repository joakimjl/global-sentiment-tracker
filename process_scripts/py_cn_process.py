from requests_html import HTMLSession
import json


"""
session = HTMLSession()

r = session.get('https://news.feedspot.com/chinese_news_websites/')

print(r)

print(r.html.render())

the_html = r.html

out_file = open("dumpedjson.json","w")

json.dump(the_html,out_file,indent=2)

out_file.close()
W
"""

in_file = open("json_files\dumpedjson.json","r")

res = json.load(in_file)

in_file.close()

found_vals = []

res_arr = []

res = res.replace("\n", " ")

for i in range(len(res)):
    if res[i:i+12] == "Media Outlet":

        temp_res = res[i+13:i+170].split(" ")

        if temp_res[0] == 'Contact':#End of website
            break

        remove_words = ["Twitter","Instagram"]

        res_dict = {
            "domain" : "",
            "facebook_fol" : "",
            "twitter_fol" : "",
            "insta_fol" : "",
            "freq_post" : "",
            "domain_auth" : "",
        }

        def removed_name_string(given_str):
            if "Twitter" in given_str:
                return given_str[0:len(given_str)-len("Twitter")]
            elif "Instagram" in given_str:
                return given_str[0:len(given_str)-len("Instagram")]
            return given_str
 
        res_dict['domain'] = temp_res[0] 
        for j in range(1,len(temp_res)):
            if "Facebook" in temp_res[j]:
                res_str = removed_name_string(temp_res[j+2])
                res_dict["facebook_fol"] = res_str
            
            if "Twitter" in temp_res[j]:
                res_str = removed_name_string(temp_res[j+2])
                res_dict["twitter_fol"] = res_str

            if "Instagram" in temp_res[j]:
                res_str = removed_name_string(temp_res[j+2])
                res_dict["insta_fol"] = res_str

            if "Frequency" in temp_res[j]:
                res_dict["freq_post"] = str(temp_res[j+1] + temp_res[j+2])

            if "Domain" in temp_res[j]:
                res_dict["domain_auth"] = str(temp_res[j+2])
        if res_dict["domain_auth"] == "" or res_dict["domain"] == "nytimes.com":
            continue
        if res_dict["domain"] != "bbc.com" and int(res_dict["domain_auth"]) >= 60:
            res_arr.append(res_dict)

res_arr = sorted(res_arr, key=lambda d: d['domain_auth'])[::-1]

print(len(res_arr))

out_file = open("json_files\cn_cleaned.json","w")

json.dump(res_arr,out_file,indent=1)

out_file.close()


