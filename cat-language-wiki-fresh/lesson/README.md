# Cat Language Wiki｜教學簡報

解壓後，開啟 `lesson/slides.html`。檔案、樣式、腳本及插圖均在專案中，請維持原資料夾結構。使用上下頁按鈕或鍵盤左右方向鍵，展開各頁「來源」可查看 Wiki 條目、來源卡與原始資料連結。原始網站連結需要網路。

若瀏覽器的管理政策禁止直接開啟本機檔案，在解壓後的專案根目錄執行 `python3 -m http.server 8000 --bind 127.0.0.1`，然後在瀏覽器開啟 `http://127.0.0.1:8000/lesson/slides.html`。

- [教學大綱與來源對照](outline.md)
- [Graph 與 Loop](workflow.md)
- [檢查報告與反思](report.md)
- [第一階段 Wiki 索引](../wiki/index.md)
- [第一階段 ingest 紀錄](../wiki/log.md)

要從逐頁草稿重建 HTML，在專案根目錄執行 `python3 lesson/build.py`。
