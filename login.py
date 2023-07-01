from io import BytesIO
from selenium import webdriver
import time
from selenium.webdriver import ActionChains
from PIL import Image


def compare_pixel(image1, image2, i, j):
    # 判断两个像素是否相同
    # 返回的值是RGB的值
    # i和j表示图片的横坐标和纵坐标
    pixel1 = image1.load()[i, j]
    pixel2 = image2.load()[i, j]
    # 阈值
    threshold = 30
    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
            pixel1[2] - pixel2[2]) < threshold:
        return True
    else:
        return False


# 实现登录
def login(url):
    # 打开360浏览器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = r"C:\Users\hfj\AppData\Roaming\360se6\Application\360se.exe"  # 这里是360安全浏览器的路径
    chrome_options.add_argument(r'--lang=zh-CN')  # 这里添加一些启动的参数
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    driver.maximize_window()
    # 点击登录按钮
    time.sleep(4)
    login_btn = driver.find_element_by_xpath('//*[@id="page-container"]/div[1]/div/div[1]/div[2]/div/div[5]/span')
    login_btn.click()
    # 跳转到输入账号密码登录页面
    time.sleep(2)
    login_change = driver.find_element_by_xpath('//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[2]')
    login_change.click()
    # 点击账号密码跳转到输入账号密码页面
    time.sleep(2)
    login_change = driver.find_element_by_xpath(
        '//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[2]')
    login_change.click()
    # 输入账号
    time.sleep(2)
    inputuid = driver.find_element_by_xpath(
        '//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/div[1]/input')
    inputuid.send_keys('19871573603')
    # 输入密码
    time.sleep(2)
    inputpassword = driver.find_element_by_xpath(
        '//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/input')
    inputpassword.send_keys('19871573603!')
    # 勾选用户协议
    time.sleep(2)
    login_change = driver.find_element_by_xpath(
        '//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[3]/input')  # 由于获取不到登录按钮，于是直接执行登录按钮对应的js代码
    login_change.click()
    # 点击登录
    time.sleep(2)
    login_change = driver.find_element_by_xpath(
        '//*[@id="J_Modal_Container"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/button')  # 由于获取不到登录按钮，于是直接执行登录按钮对应的js代码
    login_change.click()
    # 获取图片左上角位置以及图片大小
    time.sleep(2)
    img = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/div[1]')
    location = img.location
    # print("图片的位置", location)
    size = img.size
    # print("图片的大小",size)
    # 得到图片的坐标
    top, buttom, left, right = location["y"], location["y"]+size["height"], location["x"], location["x"]+size["width"]
    # print(top, buttom, left, right)
    # 截取滑块验证码的完整图片
    scrennshot = driver.get_screenshot_as_png()
    scrennshot = Image.open(BytesIO(scrennshot))
    captcha1 = scrennshot.crop((int(left), int(top), int(right), int(buttom)))
    captcha1.save('./yanzhengma.png')
    # 单击滑块按钮得到缺口图片并截图
    slider = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div[2]')
    ActionChains(driver).click_and_hold(slider).perform()
    time.sleep(1)
    scrennshot = driver.get_screenshot_as_png()
    scrennshot = Image.open(BytesIO(scrennshot))
    captcha2 = scrennshot.crop((int(left), int(top), int(right), int(buttom)))
    captcha2.save('./yanzhengma2.png')
    time.sleep(2)
    # 从滑块的右侧开始逐一比对RGB值来寻找缺口位置
    left = 77
    has_find = False
    # i和j分别是图片的横坐标和纵坐标
    for i in range(left, captcha1.size[0]):
        if has_find:
            break
        for j in range(captcha1.size[1]):
            if not compare_pixel(captcha1, captcha2, i, j):
                left = i  # 进入这个if条件即表示寻到了缺口所在的位置，将缺口的横坐标赋值给left
                has_find = True
                break
    # 需要移动的距离减去滑块距离左边边框的位置从而得到实际需要移动的距离
    move = left - 20
    # 拖动滑块到缺口位置
    ActionChains(driver).move_by_offset(xoffset=move, yoffset=0).perform()
    # time.sleep(1)
    # 将滑块滑动到缺口的位置，然后停留三秒钟
    ActionChains(driver).pause(3).perform()
    # 松开滑块
    ActionChains(driver).release().perform()
    time.sleep(10)
    # 关闭页面
    driver.quit()


if __name__ == '__main__':
    login('https://www.tianyancha.com/?jsid=SEM-BAIDU-PZ-SY-2021112-JRGW')
