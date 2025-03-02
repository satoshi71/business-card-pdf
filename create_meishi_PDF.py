import os
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image  # 画像サイズ取得用

# Gemini APIキーを設定
genai.configure(api_key="YOUR_API_KEY")

# 日本語フォントを登録（フォントパスを指定）
pdfmetrics.registerFont(TTFont("meiryo", "Trueフォントのフルパス")) 

# モデルを設定（画像認識には"gemini-pro-vision"を使用）
model = genai.GenerativeModel('gemini-1.5-flash')

# プロンプト（質問）を設定
prompt = "テキストを抽出して項目別に列挙してください。また、「filename」という項目で'会社名_氏名'という文字列を作ってください。"

# 対象の拡張子
image_extensions = ('.jpeg', '.jpg', '.png')
 
# 使用例
folder_path = "img/"  # フォルダパスを指定
 
# フォルダ内のファイル一覧を取得
files = [f for f in os.listdir(folder_path) 
    if f.lower().endswith(image_extensions)]
 
for file in files:
    # 画像ファイルを読み込み
    img = Image.open('img/'+file)
    # 画像とプロンプトをモデルに送信し、応答を取得\
    response = model.generate_content([prompt, img])
    filtered_lines = [line for line in response.text.splitlines() if line.startswith('*')]
    filename = ''
    for i in range(len(filtered_lines)):
       filtered_lines[i] = filtered_lines[i].replace('*', '')
       if filtered_lines[i].find('filename:')>=0:
          filename = filtered_lines[i].replace('filename:', '')
          filename = filename.replace(' ', '')

    # PDFを作成
    pdf_filename = 'pdf/' + filename + ".pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)

    # 画像を追加
    image_path = file  # 画像ファイルのパス
    # 画像の元のサイズを取得
    with Image.open('img/' + image_path) as img:
       orig_width, orig_height = img.size  # 元の画像の幅と高さ

    # 描画領域の幅を指定
    max_width = 400

    # 縦横比を維持して高さを計算
    aspect_ratio = orig_height / orig_width
    new_width = max_width
    new_height = max_width * aspect_ratio  # 高さを計算

    # 画像を追加（縦横比を維持）
    c.drawImage('img/' + image_path, 100, 800 - new_height, width=new_width, height=new_height, preserveAspectRatio=True, anchor='sw')

    # テキストを追加
    c.setFont("meiryo", 11)
    for i in range(len(filtered_lines)):
       c.drawString(100, 500-i*25, filtered_lines[i])

    # PDFを保存
    c.showPage()
    c.save()

    print(f"PDF '{pdf_filename}' を作成しました。")
