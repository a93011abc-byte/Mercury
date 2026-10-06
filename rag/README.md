# RAG 入門（離線可跑）

這是一個放在 `rag/` 裡的小型檢索增強生成（RAG）入門程式，跟上層的 Vue 應用分開。它會：

1. 讀取 `rag/data/` 裡的 `.md`、`.markdown`、`.txt`
2. 把文件切成有重疊的片段，並保留來源檔名、標題、片段索引
3. 用字元 n-gram 的 TF-IDF 做成**本地向量**，寫進 `rag/index/store.json`
4. 取出最相近的 top-k 片段
5. **預設不需要 API 金鑰**：直接摘錄檢索到的片段原文，並標上片段編號（例如 `01-library-rules.md#0`）
6. 若沒有相關片段，回答固定這一句，不另外編造：

> 目前的語料庫無法支持這個問題的答案。

向量是本地算的稀疏 TF-IDF，不是下載的神經網路嵌入模型。索引是一份 JSON，搜尋時做餘弦相似度的線性掃描，適合這份小語料。不需要連外網就能 ingest、提問、跑評估。

## 環境

- Python 3.11 或以上（此專案在 3.12 驗證）
- 不必安裝第三方套件，也不必下載模型

在 `rag/` 目錄執行。若希望安裝步驟有個明確指令，可以跑下面這行，它不會裝任何套件：

```bash
cd rag
python3 -m pip install -r requirements.txt
```

## 建立索引

`data/` 裡已經有三份短範例，離線就能跑：

- `01-library-rules.md`：市立圖書館借閱規則
- `02-chunking.md`：切塊、重疊、片段來源資訊
- `03-starter-scope.md`：這個入門程式實際做了什麼、沒做什麼

```bash
cd rag
python3 -m rag_app ingest
```

成功時會印出檔案數與片段數，並寫入 `index/store.json`。這個檔已列入 `rag/.gitignore`，換文件後要自己重建。

切塊參數在 `rag_app/config.py`：窗口約 320 字元，相鄰片段重疊約 60 字元。短檔不會被硬切。每個片段的編號是 `檔名#索引`，索引從 0 開始。標題取自檔案第一個 `# 標題`。

## 提問

```bash
cd rag
python3 -m rag_app ask "圖書館一次最多可以借幾本書？"
python3 -m rag_app ask "相鄰片段為什麼要保留重疊？" --k 3
```

有相關片段時，輸出會帶片段編號。摘錄的是該片段裡與問題最相近的小節原文，不是模型改寫過的句子。同一個片段若涵蓋好幾個小節，不會把沒對上的小節一起倒出來。

故意問語料裡沒有的事，應該只得到拒絕回答，而不是猜測：

```bash
python3 -m rag_app ask "量子電腦的股價何時上市？"
```

## 評估

`eval/questions.json` 有 5 題，每題標了預期的來源檔名。腳本對每題取 top-k，計算預期檔有多少出現在檢索結果裡（recall@k），並印出平均。

```bash
cd rag
python3 -m rag_app eval
```

輸出類似：

```text
retrieval recall@3
q1  recall=1.000  score=0.420  expected=01-library-rules.md  retrieved=01-library-rules.md
...
retrieval recall@3 = 1.000  (5 questions)
```

平均不到 1 時，程序以結束碼 1 離開。`--k` 可暫時覆寫題目檔裡的 k。評估看的是排序結果，不會因為拒絕回答的門檻把檔案濾掉。

## 換成自己的文件

1. 把 `.md` 或 `.txt` 放進 `rag/data/`，可以放在子資料夾。檔名（含相對路徑）就是來源檔編號。
2. 若不希望範例被檢索到，刪掉或移走 `data/` 裡的範例。
3. 重新執行 `python3 -m rag_app ingest`。這次會**整份重建**索引。
4. 用 `python3 -m rag_app ask "你的問題"` 試問。
5. 可編輯 `eval/questions.json`，把 `expected_files` 改成你的檔名，再跑 `eval`。

`data/` 只讀文字與 Markdown，不解析 PDF、HTML 或掃描圖。

## 選用的外部生成器（預設關閉）

預設不會讀取任何 API 金鑰，也不會因為環境裡剛好有別的金鑰就去呼叫模型。只有同時成立才會改走 OpenAI 相容的 Chat Completions：

| 變數 | 說明 |
| --- | --- |
| `RAG_LLM_ENABLED` | 設成 `1` 才啟用。未設定或其他值都保持摘錄回答 |
| `RAG_LLM_BASE_URL` | 相容 API 的基底網址，要含提供者要求的前綴，例如 `https://api.openai.com/v1` |
| `RAG_LLM_API_KEY` | 該介面的金鑰 |
| `RAG_LLM_MODEL` | 模型名稱。省略時用 `gpt-4o-mini` |

程式會對 `{RAG_LLM_BASE_URL}/chat/completions` 送 POST。模型只能根據檢索到的片段作答，並引用片段編號。呼叫失敗時會在標準錯誤印出原因，然後改回摘錄回答，仍然不會憑空作答。沒有檢索到相關片段時，不會去呼叫模型。

```bash
cd rag
RAG_LLM_ENABLED=1 \
RAG_LLM_BASE_URL="https://api.openai.com/v1" \
RAG_LLM_API_KEY="sk-..." \
RAG_LLM_MODEL="gpt-4o-mini" \
python3 -m rag_app ask "圖書館一次最多可以借幾本書？"
```

這需要你自己的金鑰與網路，不在離線示範的路徑上。

## 這個版本還沒有的東西

下列功能**沒有**實作，文件與程式都不要把它們當成已經可用：

- **混合檢索（hybrid search）**：沒有關鍵字索引，也沒有和向量分數的融合
- **重排序（reranking）**：沒有第二階段的交叉編碼器或其他重排
- **身分驗證（auth）**：沒有登入、權限或存取控制
- **增量索引更新**：每次 `ingest` 都是全量重建 `index/store.json`，不會只更新有改過的檔案

也還沒有網頁介面、服務行程，或近似最近鄰資料庫。語料變大以後，線性掃描這份 JSON 會變慢；那是後續的事。
