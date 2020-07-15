import json
import os

def nomalizeListJobFunction(website, in_list = []):
    """Accept a list of job functions text from websites.

    Return list of normalized job function and assign standardised code(ID)

    :param website: codename of job ads website
    :param in_list: a list contain the text of job functions (default [])
    :returns: {
        allcode,
        list
    }
    :rtype: dict
    """
    allcode = []
    new_list = []
    if len(website) < 3:
        raise Exception("Parameter 'website' error.")

    # Normalize the text according to the format from different websites
    for item in in_list:
        if website == "jobsdb":
            # Transforming input
            new_item = item.replace(">", "  (  ")
            new_item = new_item.replace("  ", " ").replace("  ", " ")

            # Mapping
            tmp_code = jobFunctionCode(website, new_item)

            # Collection
            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue

        if website == "indeed":
            continue

        if website == "cpjobs":
            tmp_code = jobFunctionCode(website, item)

            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue

        if website == "glassdoor_update":
            # Mapping
            tmp_code = jobFunctionCode(website, item)

            # Collection
            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue

        if website == "jora":
            continue

        if website == "adecco":
            continue

        if website == "michaelpage":
            # Mapping
            tmp_code = jobFunctionCode(website, item)

            # Collection
            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue

        if website == "efc":
            # Transforming input
            new_item = item

            # Mapping
            tmp_code = jobFunctionCode(website, new_item)

            # Collection
            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue

        if website == "pagepersonnel":
            # Mapping
            tmp_code = jobFunctionCode(website, item)

            # Collection
            new_list.append(tmp_code)
            allcode.append(tmp_code["code"])
            continue


    return {
        "allcode": ",".join(sorted(allcode)),
        "list": new_list
    }

def jobFunctionCode(website, in_str):
    """Accept a string of job functions text from websites.

    Return normalized job function and assign standardised code(ID)

    :param website: codename of job ads website
    :param in_str: text of job functions
    :returns: new_code
    :rtype: dict
    """
    in_str = in_str if in_str is not None else ''
    new_str = in_str
    new_code = in_str
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs_func_map.json")
    jobFuncMap = loadJson(path)

    # Load mapping set for website
    website = website.replace("_update", "")
    themapping = jobFuncMap[website]

    # 1st attempt
    if new_str not in themapping.keys():
        # do some cleaning
        new_str = in_str.replace("  ", " ").replace("&amp;", "&")

    # 2nd attempt
    if new_str not in themapping.keys():
        print(f"New category: {new_str}")
        new_code = {
            "code": "u9",
            "name": f"(New) - {new_str}",
            "orig": in_str
        }
    else:
        new_code = {
            "code": themapping[new_str]["code"],
            "name": themapping[new_str]["name"],
            "orig": in_str
        }

    return new_code

def loadJson(path):
    """Load a JSON file an return a dict object.

    :param path: relative path relative to the scrapy project root
    :returns: ajson
    :rtype: dict
    """
    ajson = {}
    with open(path, mode="r", encoding="utf8") as f:
        atext = f.read()
        try:
            ajson = json.loads(atext)
        except Exception as e:
            print(f"Error in loading JSON.", e)
    return ajson


if __name__ == "__main__":
    # Some tests
    assert jobFunctionCode("glassdoor", "Customer Services & Support")["code"] == "r6"
    assert jobFunctionCode("michaelpage", "Healthcare (Private Care)")["code"] == "d5"
    print("~~ fin. ~~")
