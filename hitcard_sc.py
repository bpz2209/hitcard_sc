import time, json, os
import getpass
from selenium import webdriver
from PIL import Image
from aip import AipOcr
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


def get_date ():
    """Get current date"""
    today = datetime.date.today()
    return "%4d%02d%02d" % (today.year, today.month, today.day)


def codeinput (driver):
    # 定位验证码位置及大小
    driver.get_screenshot_as_file('./screen.png')
    png = driver.find_element_by_id('codeImg')
    # png.screenshot('code.png')
    size = driver.get_window_size()
    left = int(size['width'] / 2) + 10
    top = int(size['height'] / 2)
    right = left + png.size['width'] + 50
    bottom = top + png.size['height'] + 30
    img = Image.open('./screen.png').crop((left, top, right, bottom))
    # img=Image.open('code.png')
    img = img.convert('L')  # P模式转换为L模式(灰度模式默认阈值127)
    count = 165  # 设定阈值
    table = []
    for i in range(256):
        if i < count:
            table.append(0)
        else:
            table.append(1)

    img = img.point(table, '1')
    img.save('code.png')
    # 识别码
    APP_ID = '24149525'
    API_KEY = 'jGkuOv07B8bXn04MTTkc3w8a'
    SECRET_KEY = 'ITNSvNarI4MSzk1M1g1ixzKuTMYVFeoi'
    # 初始化对象
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    # 读取图片
    def get_file_content (file_path):
        with open(file_path, 'rb') as f:
            return f.read()

    image = get_file_content('code.png')
    # 定义参数变量
    options = { 'language_type': 'ENG', }  # 识别语言类型，默认为'CHN_ENG'中英文混合
    #  调用通用文字识别
    result = client.basicGeneral(image, options)  # 高精度接口 basicAccurate
    for word in result['words_result']:
        code = (word['words'])

    print('验证码：' + code)

    return code


def fill_select (driver,vaccine):
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[6]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[8]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[10]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[14]/label[1]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[19]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[21]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[24]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[26]/label[2]/div[1]/p').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[2]/div[1]/div[29]/label[5]/div[1]/p').click()
    if vaccine == 1:
        driver.find_element_by_xpath('//*[@id="vaccination"]/div[2]/label[2]/div[1]/p').click()
    elif vaccine==0:
        driver.find_element_by_xpath('//*[@id="vaccination"]/div[2]/label[3]/div[1]/p').click()
    elif vaccine ==2:
        driver.find_element_by_xpath('//*[@id="vaccination"]/div[2]/label[1]/div[1]/p').click()

    driver.find_element_by_xpath('//*[@id="submit"]').click()
    driver.get_screenshot_as_file('result.png')
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="cofirmSubmit"]').click()


def login (driver, username, password, vaccine, login_url):
    element = driver.find_element_by_class_name('user-login')
    driver.execute_script("arguments[0].click();", element)
    driver.find_element_by_id('username').click()
    driver.find_element_by_id('username').clear()
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').click()
    driver.find_element_by_id('password').clear()
    driver.find_element_by_id('password').send_keys(password)
    code = codeinput(driver=driver)
    driver.find_element_by_id('imageCodeName').click()
    driver.find_element_by_id('imageCodeName').clear()
    driver.find_element_by_id('imageCodeName').send_keys(code)
    time.sleep(1)
    driver.find_element_by_class_name('login_circle').click()
    driver.get_screenshot_as_file('jiemian.png')
    try:
        alertObject = driver.switch_to.alert
        alertObject.accept()
    except:
        pass
    try:
        is_hit = driver.find_element_by_class_name('weui_msg_title')
        if is_hit.text == '您今日已上报成功，无须重复上报，感谢您的配合!':
            print('今天打过了')
    except:
        if driver.find_elements_by_class_name('error_icon') == []:
            print('登入成功')
            fill_select(driver,vaccine)

        else:
            print('trying again')
            time.sleep(1)
            driver.get(login_url)
            login(driver, username, password, login_url)
            time.sleep(1)


def main (username, password, vaccine):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')  # 这个配置很重要
    driver = webdriver.Chrome(chrome_options=chrome_options)  # 如果没有把chromedriver加入到PATH中，就需要指明路径
    login_url = 'https://login.sufe.edu.cn/cas/login?service=http%3A%2F%2Fstu.sufe.edu.cn%2Fstu%2Fsso%2Flogin%3FSsoClientServiceURI%3DaHR0cDovL3N0dS5zdWZlLmVkdS5jbi9zdHUvbmNwL25jcEluZGV4LmpzcA%3D%3D'
    driver.get(login_url)
    login(driver, username, password, vaccine, login_url)


if __name__ == '__main__':
    if os.path.exists('./config.json'):
        print("\n[Time] %s\n" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(" 打卡任务启动 ")
        configs = json.loads(open('./config.json', 'r').read())
        username = configs["username"]
        password = configs["password"]
        hour = configs["hour"]
        minute = configs["minute"]
        vaccine = configs['vaccine']

    else:
        msg = dict()
        username = input("👤 上财统一认证用户名: ")
        msg['username'] = username
        password = input('🔑 上财统一认证密码: ')
        msg['password'] = password
        print("⏲ 请输入定时时间（默认每天6:05）")
        hour = input("\thour: ") or 6
        minute = input("\tminute: ") or 5
        msg['hour'] = hour
        msg['minute'] = minute
        vaccine = input('\t接种针数{ 未接种:0, 接种一针:1, 两针:2}')
        msg['vaccine'] = vaccine
        with open('./config.json', 'w') as file:
            json.dump(msg, file)
    main(username, password)
    print("\n[Time] %s\n" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(" 打卡任务启动 ")
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', args=[username, password, vaccine], hour=hour, minute=minute)
    print('⏰ 已启动定时打卡服务，每天 %02d:%02d 为您打卡' % (int(hour), int(minute)))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
