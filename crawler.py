import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def get_mamibuy_articles():
    """上網抓取 MamiBuy 媽咪拜最新的育兒文章"""
    url = "https://mamibuy.com.tw/talk/article/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抓取文章區塊（根據 MamiBuy 目前網頁結構抓取最新文章標題與連結）
        articles = soup.find_all('a', class_='extend-fllow-title')
        
        content_list = []
        # 只取前 5 篇精選文章
        for art in articles[:5]:
            title = art.get_text().strip()
            link = "https://mamibuy.com.tw" + art['href']
            content_list.append(f"📌 【{title}】\n🔗 傳送門：{link}\n")
            
        if not content_list:
            # 如果結構有變，抓備用的熱門排行區塊
            backup_articles = soup.find_all('div', class_='text-box')
            for art in backup_articles[:5]:
                a_tag = art.find('a')
                if a_tag:
                    title = a_tag.get_text().strip()
                    link = "https://mamibuy.com.tw" + a_tag['href']
                    content_list.append(f"📌 【{title}】\n🔗 傳送門：{link}\n")
                    
        return "\n".join(content_list)
    except Exception as e:
        print(f"抓取文章失敗: {e}")
        return "暫時無法取得最新育兒文章，請稍後再試。"

def send_email(article_content):
    """透過 Gmail 發送精華週報到你的信箱"""
    # 從 GitHub 保險箱（Secrets）讀取你剛剛設定的帳密
    gmail_user = os.environ.get('MY_EMAIL')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("錯誤：保險箱密碼讀取失敗，請檢查 Settings 設定！")
        return

    # 設定 Email 內容與排版
    msg_text = f"""
    🌸 親愛的，您本週的專屬育兒情報已送達 🌸
    
    GitHub 雲端機器人已經幫您巡邏完畢！
    以下是為您精選的《MamiBuy 媽咪拜》最新熱門育兒教養文章：
    
    --------------------------------------------------
    {article_content}
    --------------------------------------------------
    
    祝您今天也是美好、順心的一天！💕
    -- 您的專屬 GitHub 智慧育兒助理
    """
    
    msg = MIMEText(msg_text, 'plain', 'utf-8')
    msg['Subject'] = Header('🌸 本週育兒熱門教養新知情報 🌸', 'utf-8')
    msg['From'] = gmail_user
    msg['To'] = gmail_user

    try:
        # 連線到 Gmail 官方發信伺服器
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, [gmail_user], msg.as_string())
        server.quit()
        print("🎉 Email 順利寄出囉！快去信箱收信吧！")
    except Exception as e:
        print(f"Email 寄送失敗: {e}")

if __name__ == "__main__":
    print("🤖 機器人開機，正在為您蒐集育兒新知...")
    articles = get_mamibuy_articles()
    send_email(articles)
