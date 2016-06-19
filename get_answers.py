import requests, json
from bs4 import BeautifulSoup
question_id = 59702

def get_answers(q_id, page_id = 1):
    url = 'http://api.stackexchange.com/2.2/questions/%d/answers'%question_id
    values = {"page":str(page_id),
              "order":"desc",
              "sort":"activity",
              "site":"codegolf",
              "filter": "!SWJ_BpAceOT6L*G2Qa"}
    response = requests.get(url, params=values)
    response_dict = response.json()
    answers = response_dict["items"]
    print "QUOTA", response_dict["quota_remaining"], "OF", response_dict["quota_max"]
    if response_dict["has_more"]:
        answers.extend(get_answers(q_id, page_id+1))
    return answers

def get_answer_body(q_id=question_id):
    answers = get_answers(q_id)
    return [answer["body"] for answer in answers]

def get_extention(language):
    language = language.lower()
    languages = {
        "python": "py",
        "python 2": "py",
        "python 3": "py",
        "java": "java",
        "ruby": "rb",
        "awk": "awk",
        "node.js": "js",
        "coffeescript": "coffee",
        "bash": "sh",
        "sh": "sh",
        "c++": "cpp",
        "r": "r"
        }
    if language in languages:
        return languages[language]
    return ""

def parse_answer(body):
    soup = BeautifulSoup(body, "html5lib")
    header = soup.get_text().split("\n")[0]
    code_xml = soup.find("code")
    parts = header.split(",")
    if len(parts) != 2:
        print "ANSWER DOESN'T HAVE VALID HEADER" , `header`
        return
    if not code_xml:
        print "ANSWER DOESN'T HAVE VALID CODE BLOCK", `header`
        return
    bot_name, language = [part.strip() for part in parts]
    code = code_xml.get_text()
    extention = get_extention(language)
    if extention == "":
        try:
            print "UNKNOWN LANGUAGE", language
        except UnicodeEncodeError:
            print `language`
        return
    bot_name = "".join(x for x in bot_name if x.isalnum())
    file_name = bot_name+"."+extention
    return bot_name, file_name, extention, language, code

def save_answer(entry):
    #print entry
    try:
        f = open("bots/"+entry[1], "w")
    except UnicodeEncodeError:
        f = open("bots/"+`entry[1]`, "w")
    f.write(entry[4].encode("UTF-8"))
    f.close()
    return ['sh', './commands/%s.sh'%entry[3].lower(), './bots/%s'%entry[1], entry[0]]

answers = map(save_answer, filter(None,map(parse_answer, get_answer_body())))
#print(answers)
f = open("answers.json", "w")
json.dump(answers, f)
f.close()
print len(answers)

