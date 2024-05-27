import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証情報のパス（JSONファイル）を指定
credentials_path = 'scraping\spread-sheet-api-419202-59ee0bee5075.json'

# スプレッドシートのURL
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1qjYieNxp0gG3fOuDNkV46DL4Q1wK8vn_kcZTiYwtVIw/edit'

# 認証情報を読み込む
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(credentials)

# スプレッドシートを開く
sheet = client.open_by_url(spreadsheet_url).sheet1

# データを取得
data = sheet.get_all_records()

