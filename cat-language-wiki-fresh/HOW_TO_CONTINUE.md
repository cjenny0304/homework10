# 下一步｜批次 ingest 操作

1. 以 Coding Agent 開啟整個專案根目錄，先閱讀 `requirements.md`、`AGENTS.md`、`sources.json`、`logs/source_review.md`。
2. 請先逐一打開 S01…S07 的原始 URL，視權限下載可用全文／網頁，記錄 `raw/` 內可以被讀取的檔案類型；不允許假裝下載成功。
3. 在仍符合原本決定「一次匯入所有資料」前提下，將七份合格資料在**同一批次**交由 AI 編纂成 `wiki/topics/*.md`；每個條目標示來源 ID、支持內容與限制。
4. 批次完成再逐筆執行來源核對、編號與完整性檢查；填入 `wiki/log.md`。
5. 只有成功 ingest >= 5 筆且通過檢查，才可進入下一階段大綱、證據卡與 HTML。先前 HTML 不沿用。
6. 儲存 git commit 以保留階段證據；下一階段再設計具體 Graph 退回路線，實際跑一輪並填 `report.md`。

## 可直接貼到 Codex 的指令
請閱讀 AGENTS.md、requirements.md、sources.json、logs/source_review.md。這是全新專案，已完成 8 題討論並確認需求，禁止沿用舊版輸出。先檢查 raw/ 的 7 張來源導讀卡與原始連結，能合法取得全文者請下載並核對，不能取得則保留摘要層級與限制。請提出執行計畫後，依使用者要求「一次批次 ingest 七份資料」，產出有來源追溯的 wiki/topics/*.md，將真實成功／失敗及證據寫進 wiki/log.md。接著執行來源驗證與覆蓋率檢查。此輪先不要產生 HTML。若沒有足夠可讀內容，不要宣稱 ingest 成功。
