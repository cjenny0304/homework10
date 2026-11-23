# Wiki 批次 ingest 紀錄

- 開始：2026-11-23T13:40:21+08:00
- 執行：Codex 編輯核對後的來源筆記，以 Python 單次寫入全部五篇條目及索引。
- 完成：2026-11-23T13:40:21+08:00

| 來源 | 結果 | 材料層級 | 條目 |
|---|---|---|---|
| [S01](../raw/S01.md) | SUCCESS | 全文（開放授權 PDF） | [speech](topics/speech.md), [myths](topics/myths.md) |
| [S02](../raw/S02.md) | SUCCESS | 出版社摘要 | [speech](topics/speech.md) |
| [S03](../raw/S03.md) | SUCCESS | 大學典藏作者稿全文、出版社摘要及更正公告 | [speech](topics/speech.md) |
| [S04](../raw/S04.md) | SUCCESS | 全文（開放授權 PDF） | [emotions](topics/emotions.md), [myths](topics/myths.md) |
| [S05](../raw/S05.md) | SUCCESS | 官方照護網頁 | [body-language](topics/body-language.md), [emotions](topics/emotions.md), [myths](topics/myths.md) |
| [S06](../raw/S06.md) | SUCCESS | 官方知識庫網頁 | [body-language](topics/body-language.md), [myths](topics/myths.md), [daily-habits](topics/daily-habits.md) |
| [S07](../raw/S07.md) | SUCCESS | 官方獸醫手冊網頁 | [daily-habits](topics/daily-habits.md) |

批次結果為 7 成功、0 失敗、0 阻擋。取得全文遇到的限制見[來源核實紀錄](../logs/source_review.md)。

來源完整性、內容覆蓋及修正重驗見[驗證報告](../report.md)。

初次完整性檢查發現相鄰引用會合併，已局部修正標記。重驗為 5/5 主題、7/7 來源，50 個內文引文均能各自解析。
