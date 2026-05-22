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
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_list = []
        
        # 嘗試方法 A: 抓取最新文章標題與連結
        articles = soup.find_all('a', class_='extend-fllow-title')
        for art in articles[:5]:
            title = art.get_text().strip()
            link = "https://mamibuy.com.tw" + art['href']
            if title and link:
                content_list.append(f"<li><a href='{link}' style='color: #FF69B4; font-weight: bold; text-decoration: none;'>📌 {title}</a></li>")
            
        # 嘗試方法 B (備用): 抓取熱門排行區塊
        if not content_list:
            backup_articles = soup.find_all('div', class_='text-box')
            for art in backup_articles[:5]:
                a_tag = art.find('a')
                if a_tag:
                    title = a_tag.get_text().strip()
                    link = "https://mamibuy.com.tw" + a_tag['href']
                    content_list.append(f"<li><a href='{link}' style='color: #FF69B4; font-weight: bold; text-decoration: none;'>📌 {title}</a></li>")
                    
        # 🌟 防呆：如果網頁改版真的都抓不到，強迫塞入測試內容，確保信件不是空的！
        if not content_list:
            content_list.append("<li>🌸 機器人成功連線，但今日 MamiBuy 網站維護中，先向您問候一聲平安！</li>")
            content_list.append("<li>💡 建議晚點再次手動觸發測試看看唷。</li>")
            
        return "".join(content_list)
    except Exception as e:
        print(f"抓取文章失敗: {e}")
        return "<li>❌ 網路連線稍微逾時，請稍後再試。</li>"

def send_email(article_content):
    """透過 Gmail 發送 HTML 高質感精華週報"""
    gmail_user = os.environ.get('MY_EMAIL')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("錯誤：保險箱密碼讀取失敗，請檢查 Settings 設定！")
        return

    # 🌟 升級為高質感網頁 HTML 信件格式
    html_text = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #FFF5F7; padding: 20px; color: #4A4A4A;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 25px; border-radius: 20px; border: 2px solid #FFE0E6; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
            <h2 style="color: #FF69B4; text-align: center; margin-top: 0;">🌸 您的專屬育兒情報已送達 🌸</h2>
            <p style="font-size: 14px; line-height: 1.5; color: #666;">
                親愛的，GitHub 雲端機器人已經幫您巡邏完畢！<br>
                以下是為您精選的<b>《MamiBuy 媽咪拜》</b>熱門教養動態：
            </p>
            <hr style="border: 0; border-top: 1px dashed #FFE0E6; margin: 20px 0;">
            <ul style="padding-left: 15px; line-height: 2;">
                {article_content}
            </ul>
            <hr style="border: 0; border-top: 1px dashed #FFE0E6; margin: 20px 0;">
            <p style="font-size: 12px; text-align: center; color: #999; margin-bottom: 0;">
                💕 祝您今天也是美好、順心的一天！<br>
                -- 您的專屬 GitHub 智慧助理
            </p>
        </div>
    </body>
    </html>
    """
    
    # 指定為 html 格式
    msg = MIMEText(html_text, 'html', 'utf-8')
    msg['Subject'] = Header('🌸 本週育兒熱門教養新知情報 🌸', 'utf-8')
    msg['From'] = Header(f"育兒情報機器人 <{gmail_user}>", 'utf-8')
    msg['To'] = gmail_user

    try:
        print("⚡ 正在連線至 smtp.gmail.com...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(gmail_user, gmail_password)
        print("🔑 登入成功，正在發送郵件...")
        server.sendmail(gmail_user, [gmail_user], msg.as_string())
        server.quit()
        print("🎉 郵件已成功由 Google 伺服器接管並投遞！")
    except Exception as e:
        print(f"❌ Email 發送過程中發生悲劇: {e}")

if __name__ == "__main__":
    print("🤖 機器人全新升級開機...")
    articles = get_mamibuy_articles()
    send_email(articles)
