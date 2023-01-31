from selenium import webdriver

def browser_setup(browser_name):
    '''Inizialize webdriver paramiters for a specific browser

    Parameters
    ----------
    browser_name: string
        Name of the browser, either 'Chrome' or 'Firefox'.

    Returns
    -------
    driver: selenium.webdriver
        webdriver object with paramenters for the chosen browser.

    '''
    if browser_name == 'Chrome':
        # Set driver of Chrome (requires version > 9.0)
        options = webdriver.ChromeOptions()
        # Disable popup
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    elif browser_name == 'Firefox':
        # Set driver for Firefox
        options = webdriver.FirefoxOptions()
        #Disable popup
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    return driver