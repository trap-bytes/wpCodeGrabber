from bs4 import BeautifulSoup
import requests
import argparse
import urllib.parse
import os
import threading

def download_file(url, cookies, dirname):
    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'id': 'newcontent'})
        if textarea:
            content = textarea.text.strip()
            
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            file_param = query_params.get('file')
            if file_param:
                file_path = urllib.parse.unquote(file_param[0])
            else:
                print(f"No 'file' parameter found in URL: {url}")

            with open(os.path.join(dirname, file_path), 'a') as file:
                file.write(content)
                print(f"Content added to file: {file_path}")
        else:
            print(f"No <textarea> tag with id 'newcontent' found in {url}")
    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")            

def extract_attributes(html_content, case, additional_extensions):

    base_extensions = {'php', 'js', 'html'}
    allowed_extensions = base_extensions.union(additional_extensions)
    
    soup = BeautifulSoup(html_content, 'html.parser')

    href_values = []
    for tag in soup.find_all(href=True):
        href = tag['href']
        if "file=" in href:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            if 'file' in params:
                file_path = urllib.parse.unquote(params['file'][0])
                _, file_extension = os.path.splitext(file_path)
                if file_extension.lower()[1:] in allowed_extensions:
                    href_values.append(href)


    file_values = []
    for href_value in href_values:
        params_dict = urllib.parse.parse_qs(urllib.parse.urlparse(href_value).query)
        if 'file' in params_dict:
            file_path = urllib.parse.unquote(params_dict['file'][0])
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext[1:] in allowed_extensions:
                file_values.append(file_path)

    main_directory_name = "Plugins" if case == "plugin-editor.php" else get_theme_name(href_values)
    return file_values, href_values, main_directory_name

def get_theme_name(href_values):
    theme_name = None
    for href_value in href_values:
        params_dict = urllib.parse.parse_qs(urllib.parse.urlparse(href_value).query)
        if 'theme' in params_dict:
            theme_name = params_dict['theme'][0]
    return theme_name if theme_name else "ThemeDirectory"

def recreate_directory_structure(file_values, dirname, output_dir):
    dirname = output_dir + "/" + dirname
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    for file_value in file_values:
        directories, filename = os.path.split(file_value)
        current_dir = os.path.join(dirname, directories)
        if directories and not os.path.exists(current_dir):
            os.makedirs(current_dir)
       
        file_path = os.path.join(current_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('') 

        if directories == '' and filename:
            file_path = os.path.join(dirname, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write('')

def get_plugins_urls(url, cookies):
    base_url = url + "?plugin=PLACEHOLDER&Submit=Select"
    urls = []
    response = requests.get(url, cookies=cookies)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        select_tag = soup.find('select', {'id': 'plugin'})
        
        if select_tag:
            for option_tag in select_tag.find_all('option'):
                plugin_value = option_tag['value']
                url = base_url.replace("PLACEHOLDER", plugin_value)
                urls.append(url)
        else:
            print("Select tag with id 'plugin' not found.")
    else:
        print("Failed to fetch the page. Status code:", response.status_code)

    return urls

def download_files(urls, cookies, dirname, output_dir):
    dirname = output_dir + "/" + dirname
    threads = []
    for url in urls:
        t = threading.Thread(target=download_file, args=(url, cookies, dirname))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def download_theme_files(theme_url, cookies, additional_extensions, output_dir):
    try:
        response = requests.get(theme_url, cookies=cookies)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        print("Error fetching content:", e)
        return

    file_values, urls, theme_name = extract_attributes(html_content, "theme-editor.php", additional_extensions)
    recreate_directory_structure(file_values, theme_name, output_dir)

    print("\033[1;32m\n [+] " + theme_name + " theme detected\033[0m")
    print("\033[1;32m [+] Downloading theme files\033[0m\n")

    download_files(urls, cookies, theme_name, output_dir)

def download_plugin_files(plugins_base_url, cookies, additional_extensions, output_dir):
    plugin_urls = get_plugins_urls(plugins_base_url, cookies)

    print("\033[1;32m\n [+] Downloading plugin files\033[0m\n")
    for p_url in plugin_urls:
        try:
            response = requests.get(p_url, cookies=cookies)
            response.raise_for_status()
            html_content = response.text
        except requests.RequestException as e:
            print("Error fetching content:", e)
            return

        file_values, urls, plugin_dir = extract_attributes(html_content, "plugin-editor.php", additional_extensions)
        recreate_directory_structure(file_values, plugin_dir, output_dir)
        download_files(urls, cookies, plugin_dir, output_dir)

def main():
    parser = argparse.ArgumentParser(description="Extract href attributes from HTML of a website.")
    parser.add_argument("-u", "--url", help="URL of the website")
    parser.add_argument("-c", "--cookie", help="Cookie string to be sent with the request")
    parser.add_argument("-t", "--theme", action='store_true', help="Download theme files")
    parser.add_argument("-p", "--plugin", action='store_true', help="Download plugin files")
    parser.add_argument("-e", "--extension", help="Comma separated list of additional extensions")
    parser.add_argument("-o", "--output-dir", help="Output directory")
    args = parser.parse_args()

    if not args.url:
        print("Please provide a URL using the -u/--url flag.")
        return

    if not args.cookie:
        print("Please provide cookies value using the -c/--cookie flag.")
        return

    cookies = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in args.cookie.split(";") if cookie.strip()}

    output_dir = args.output_dir or os.getcwd()

    additional_extensions = args.extension.split(",") if args.extension else []
    

    theme_url = args.url + "/wp-admin/theme-editor.php"
    plugins_base_url = args.url + "/wp-admin/plugin-editor.php"

    if args.theme:
        download_theme_files(theme_url, cookies, additional_extensions, output_dir)

    if args.plugin:
        download_plugin_files(plugins_base_url, cookies, additional_extensions, output_dir)

    if not args.theme and not args.plugin:
        download_theme_files(theme_url, cookies, additional_extensions, output_dir)
        download_plugin_files(plugins_base_url, cookies, additional_extensions, output_dir)

    print("\033[1;32m\nDownload completed\033[0m")

if __name__ == "__main__":
    main()
