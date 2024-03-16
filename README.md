# wpCodeGrabber

wpCodeGrabber is a simple script that facilitates the download of WordPress website code (Active theme + Installed plugins) directly from the wp-admin panel.
This can be particularly useful for scenarios where direct access to cPanel or the web server is not available.
Additionally, it can serve as a handy tool for auditing code for security vulnerabilities when access is limited to wp-admin panel.

Tested with WP 6.4 version.

![wpCodeGrabber](https://github.com/trap-bytes/wpCodeGrabber/blob/main/static/wpCodeGrabber.png)

## Requirements

For the script to function properly, ensure the following conditions are met:

1. Theme and Plugin Editing should be enabled from wp-admin panel (default behaviour).
2. `wordpress_sec_xxxxxxxx` cookie of a wordpress account able to edit theme and plugin from wp-admin panel (e.g. admin) should be provided.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/trap-bytes/wpCodeGrabber.git
    ```

2. Navigate to the wpCodeGrabber directory:

    ```bash
    cd wpCodeGrabber
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. To run the script:

    ```bash
    python3 wpCodeGrabber.py -u <WordPress_URL> -c "<Cookies>"
    ```

    Replace `<WordPress_URL>` with the URL of the WordPress site and `<Cookies>` with the cookie string to be sent with the request. In order to run the script, the `wordpress_sec_xxx=xyz` cookie value should be enough.

2. Optionally, you can specify additional options:
   - `-t` or `--theme`: Download theme files only.
   - `-p` or `--plugin`: Download plugin files only.
   - `-e` or `--extension`: Specify additional extensions for file types. 
   - `-o` or `--output`: Specify the output directory where the code will be saved.

## Example

To download theme files only, including _.svg_ files from a WordPress site with the URL `https://example.com` and cookie `wordpress_sec_xxx=xyz`, you would run:

```bash
python3 wpCodeGrabber.py -u https://example.com -c "wordpress_sec_xxx=xyz" -t -e svg
```

**Note:** You have to substitute the wordpress_sec_xxx cookie parameter and value with the ones returned by the Wordpress Website after login.
