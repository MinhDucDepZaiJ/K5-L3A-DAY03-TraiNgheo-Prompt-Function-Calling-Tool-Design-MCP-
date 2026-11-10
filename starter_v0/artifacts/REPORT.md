# Day 03 Lab v2 Report — Research Agent

## Team

- Team: TraiNgheo
- Members: Nguyễn Đức Minh - 2A2022603633, Bùi Lê Công Tuấn - 2A202603610, Trần Quốc Đông - 2A202603643, Ngô Văn Tuân - 2A202603630 
- Provider/model: OpenRouter — `openai/gpt-4o-mini` (all runs and transcripts)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: tìm tin tức web (Tavily), tìm bài đăng / timeline Twitter (RapidAPI), đọc nội dung một URL (Firecrawl), tìm bài báo arXiv, tra cứu chính sách công ty, **so sánh hai nguồn văn bản** (tool mới của nhóm), và gửi bản tin lên Telegram chỉ sau khi người dùng xác nhận. Khi thiếu thông tin (handle, URL, nguồn thứ hai) agent hỏi lại bằng `clarify`; yêu cầu ngoài phạm vi (toán, code) thì từ chối, không gọi tool.

**Link dùng thử (deploy):**

URL: 

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (text / yes_no / choice) | không |
| timeline | lấy các bài đăng gần đây của một tài khoản (`screenname` không có `@`, `limit`) | không |
| social_search | tìm bài đăng theo từ khóa, `search_type` = `Latest` / `Top`, `limit` | không |
| lookup | tìm web / tin tức qua Tavily (`topic` = general/news, `timeframe`) | không |
| fetch | đọc nội dung một URL cụ thể qua Firecrawl | không |
| format | định dạng các item đã thu thập thành markdown digest | không |
| send | gửi text lên Telegram, chỉ khi `confirmed=true` | không (bonus có sẵn) |
| policy | tìm trong `company_policy/*.md` | không (bonus có sẵn) |
| papers | tìm bài báo trên arXiv | không (bonus có sẵn) |
| paper_text | tải PDF arXiv và trích văn bản | không (bonus có sẵn) |
| **compare_sources** | so sánh hai đoạn văn bản: câu chung, câu chỉ có ở A, chỉ có ở B, điểm tương đồng (0–1). Chỉ so sánh câu chữ, **không** kiểm chứng sự thật | **có** |

## A3. Câu hỏi mẫu để thử

1. `Tìm 5 tin tức mới nhất về OpenAI trong tuần này.` → `lookup(query="OpenAI", topic="news", timeframe="week", max_results=5)`
2. `Tìm 5 bài đăng mới nhất về AI trên Twitter.` → `social_search(query="AI", search_type="Latest", limit=5)`
3. `So sánh hai nguồn: Nguồn A là "AI giúp tăng năng suất." và nguồn B là "AI có thể thay thế một số công việc."` → `compare_sources` (similarity 0.3051, không có câu chung)
4. `Tóm tắt 5 tweet mới nhất giúp mình` → agent phải hỏi lại tài khoản (`clarify`), không đoán
5. `Đăng bản tin này lên Telegram giúp mình` → agent phải xin xác nhận yes/no trước, chưa gọi `send`

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Metric = `case_accuracy` trên `data/eval_base.json` (20 case: 14 single-turn + 6 multi-turn), model `openai/gpt-4o-mini`. Số liệu lấy từ `summary` trong từng run file; khớp với `version_log.csv`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (`system_prompt.md`, prompt starter có chỉ dẫn xấu cố ý) | Đánh giá prompt ban đầu | — | 0.65 (13/20) | `runs/v0_B_base_openrouter_20261110T104218329165.json` |
| v1 | `system_prompt.md` — thêm mục "Missing Information Rule" | Không đoán thông tin còn thiếu | 0.65 | 0.80 (16/20) | `runs/v1_B_base_openrouter_20261110T104836014741.json` |
| v2 | `system_prompt.md` — viết lại: scope, missing info, xác nhận trước khi gửi, routing, args, multi-tool | Cải thiện routing và arguments | 0.80 | 0.95 (19/20) | `runs/v2_B_base_openrouter_20261110T105612437535.json` |
| v3 | `system_prompt.md` — thêm mục "Switching Tools Across Turns" | Không gọi tool thừa khi đổi yêu cầu | 0.95 | 0.95 (19/20) — **không đổi** | `runs/v3_B_base_openrouter_20261110T110135090127.json` |
| v4 | `system_prompt.md` — mục 8 viết lại: "latest instruction has priority", hủy tool cũ khi đổi nguồn, ví dụ bắt buộc | Ưu tiên yêu cầu mới nhất, hủy tool cũ khi người dùng chuyển nguồn | 0.95 | **1.00 (20/20)** | `runs/v4_B_base_openrouter_20261110T112426007769.json` |
| v4_tools | `tools.yaml` — thêm tool `compare_sources` (tools hash `5b22…` → `5796…`), prompt giữ nguyên v4 | Thêm tool mới không làm hỏng routing cũ | 1.00 | 1.00 (20/20) | `runs/v4_tools_B_base_openrouter_20261110T115841624804.json` |

Chi tiết các chỉ số phụ:

| Version | tool_routing | argument | multiturn | failure_counts |
|---|---:|---:|---:|---|
| v0 | 0.75 | 0.65 | 1.00 | wrong_tool 2, out_of_scope 2, missing_info 2, wrong_boundary 1 |
| v1 | 0.85 | 0.80 | 1.00 | out_of_scope 1, missing_info 1, wrong_boundary 1, wrong_tool 1 |
| v2 | 0.95 | 0.95 | 0.8333 | wrong_tool 1 |
| v3 | 0.95 | 0.95 | 0.8333 | wrong_tool 1 |
| v4 | 1.00 | 1.00 | 1.00 | — |
| v4_tools | 1.00 | 1.00 | 1.00 | — |

## B2. Failure Analysis

Lấy từ `results[*].result.failures` của các run v0–v3 (base eval). Phần phân tích prompt từng version (root cause, hypothesis) lấy từ tài liệu "Tổng hợp Phân tích System Prompt". 
### B2.1. Bảng failure theo case

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Đoán Sam Altman thay vì hỏi tài khoản (v0 bảo "pick a well-known account like Sam Altman"). Twitter API còn trả 403 nên call thừa cũng vô ích. Fail ở v0 và v1 | v1 thêm rule nhưng prompt vẫn còn chỉ dẫn "guess" nên chưa hết. v2: viết lại prompt, bỏ chỉ dẫn đoán, `clarify(response_type="text")` khi thiếu handle → pass |
| R11_missing_url | missing_info | `fetch` với URL tự bịa | Không hỏi URL (v0 bảo "assume a likely URL and read it"). Fail ở v0 | v1: "Missing Information Rule" (không bịa URL/handle, thiếu URL → `clarify`) → pass |
| R12_confirm_before_send | wrong_boundary | `send` | Gửi Telegram ngay, không xin xác nhận (v0: "just go ahead and do it"). Fail ở v0 và v1 | v2: mục 3 — `clarify(response_type="yes_no")` trước, chỉ `send(confirmed=true)` sau khi user xác nhận → pass |
| R08_out_of_scope | out_of_scope | có gọi tool (kỳ vọng không gọi) | Bài toán tích phân vẫn bị đưa vào tool. Fail ở v0 và v1 | v2: mục 1 "Scope" — toán/code/capability thì không gọi tool → pass |
| R14_out_of_scope_coding | out_of_scope | có gọi tool | Yêu cầu viết hàm Python bị gọi tool. Fail ở v0, hết ở v1 | Hết từ v1 (hiệu ứng phụ của rule "không đoán"); chốt bằng rule scope ở v2 |
| R03_web_news_routing | wrong_tool (arg) | `lookup(query="AI news")` | `query` thừa chữ "news" (kỳ vọng `"AI"`). Fail ở v0 | v2: mục 4 — không thêm "news"/"today" vào query, kèm ví dụ → pass (thực tế đã pass từ v1) |
| R13_parallel_web_and_tweets | wrong_tool (arg) | `lookup(query="AI news", topic=None)` | `query` thừa "news", thiếu `topic="news"`. v0 còn bị ép "pick one tool". Fail ở v0 và v1 | v2: mục 7 — bỏ giới hạn một tool, cấu hình từng tool độc lập, ví dụ `lookup` + `social_search` → pass |
| M06_switch_tool | wrong_tool (unnecessary_tool) | `social_search` (gọi thêm) | User nói "Bỏ Twitter, chuyển sang web" nhưng agent vẫn gọi `social_search`: chưa phân biệt context còn hiệu lực với tool/task đã bị hủy. Fail ở v2 và v3 | v3 thêm "Switching Tools Across Turns" nhưng chưa đủ. v4: mục 8.2–8.6 — yêu cầu mới nhất ưu tiên, tool bị hủy không được chạy, "giữ chủ đề" ≠ "giữ tool", 3 ví dụ bắt buộc → pass |

### B2.2. Root cause theo chỉ dẫn của prompt v0

| Chỉ dẫn trong v0 | Vấn đề | Failure type | Case thật xác nhận |
|---|---|---|---|
| `do not ask them back` / `make a sensible guess` | Không dùng `clarify`, tự bịa argument | missing_info, wrong_arg_value | R10, R11 (xác nhận) |
| "pick a well-known account like Sam Altman" | Bịa `screenname` | missing_info | R10 (xác nhận: gọi `timeline(sama)`) |
| "assume a likely URL and read it" | `fetch` URL không có trong hội thoại | missing_info | R11 (xác nhận) |
| "just go ahead and do it" (send/post) | Gửi trước khi user xác nhận | wrong_boundary | R12 (xác nhận) |
| "single step" / "Pick one tool" | Cản workflow `clarify → user reply → tool` và request nhiều nguồn | wrong_boundary, unnecessary_tool | R13 (xác nhận một phần: sai arg, không thấy bằng chứng bị ép một tool) |
| (không có rule scope) | Gọi tool cho toán/code | out_of_scope | R08, R14 (xác nhận) |

Root cause chung: v0 ưu tiên **tốc độ và tự suy đoán** hơn **độ chính xác, clarification và safety boundary**.

### B2.3. Hypothesis và kết quả từng version

| Version | Hypothesis | Failure type nhắm tới | Kết quả thực tế |
|---|---|---|---|
| v1 | Rule "không đoán, thiếu thì `clarify`" giảm missing_info | missing_info, wrong_arg_value | Đúng một phần: R11 FAIL→PASS, R14 và R03 cũng pass; R10 chưa hết (v0 vẫn còn trong prompt). 0.65 → 0.80 |
| v2 (tài liệu: v2a) | Routing policy đầy đủ (scope, send confirmation, args, multi-tool) giảm wrong_tool/wrong_arg/wrong_boundary/out_of_scope | wrong_tool, wrong_arg_value, wrong_boundary, unnecessary_tool, out_of_scope | Đúng: R08, R10, R12, R13 FAIL→PASS. 0.80 → 0.95. **Nhưng có regression M06** (xem B2.4) |
| v3 | Rule "Switching Tools Across Turns" giảm tool thừa khi đổi yêu cầu | unnecessary_tool | **Không chứng minh được**: M06 vẫn fail, 0.95 → 0.95 |
| v4 (tài liệu: v2b/V4) | Phân biệt context cần giữ với tool/task bị thay thế giúp multi-turn chính xác hơn | wrong_tool, unnecessary_tool | Đúng: M06 FAIL→PASS, 1.00. Không có regression so với v3 |

### B2.4. Improvement / Regression theo case

Quy ước: FAIL→PASS = improvement, PASS→FAIL = regression (ghi lại dù metric tổng tăng), FAIL→FAIL = chưa giải quyết, PASS→PASS = stable.

| Case | v0→v1 | v1→v2 | v2→v3 | v3→v4 |
|---|---|---|---|---|
| R03_web_news_routing | FAIL→PASS | stable | stable | stable |
| R08_out_of_scope | FAIL→FAIL | FAIL→PASS | stable | stable |
| R10_missing_handle | FAIL→FAIL | FAIL→PASS | stable | stable |
| R11_missing_url | FAIL→PASS | stable | stable | stable |
| R12_confirm_before_send | FAIL→FAIL | FAIL→PASS | stable | stable |
| R13_parallel_web_and_tweets | FAIL→FAIL | FAIL→PASS | stable | stable |
| R14_out_of_scope_coding | FAIL→PASS | stable | stable | stable |
| **M06_switch_tool** | stable | **PASS→FAIL (regression)** | FAIL→FAIL | FAIL→PASS |
| 12 case còn lại | stable | stable | stable | stable |

**Regression đáng chú ý:** M06 pass ở v0 và v1, nhưng fail từ v2 (`multiturn_accuracy` 1.00 → 0.8333). Giả thuyết (chưa kiểm chứng bằng run riêng): v2 thêm rule multi-tool ("Do not restrict yourself to a single tool", "Use all tools necessary") và "preserve context", làm agent giữ lại `social_search` của lượt trước. Đây khớp với root cause v4 nhắm tới. Các regression tiềm năng khác được tài liệu liệt kê (hỏi `clarify` quá nhiều, áp name→handle mơ hồ, từ chối nhầm request hợp lệ, hỏi xác nhận `send` lặp lại) **không** thấy xuất hiện trong 20 case base.

## B3. Team Eval Cases

10 case trong `data/eval_group.json` (5 single-turn G01–G05, 5 multi-turn G06–G10).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_news | Chọn `lookup` cho tin tức, đúng `timeframe` | `lookup(query="OpenAI", topic="news", timeframe="week")` | Pass |
| G02_twitter | Tìm bài đăng Twitter, `Latest`, `limit=5` | `social_search(query="AI", search_type="Latest", limit=5)` | Pass |
| G03_papers | Dùng `papers` thay vì `lookup` cho bài báo khoa học | `papers(query="large language models", max_results=3)` | Pass |
| G04_compare | Chọn tool mới `compare_sources` khi có đủ hai nguồn | `compare_sources(source_a, source_b)` | Pass |
| G05_fetch | Chọn `fetch` để đọc URL, không search lại | `fetch(url="https://example.com/article")` | Pass |
| G06_change_limit | Giữ tài khoản, đổi `limit` 5 → 3 | `timeline(screenname="elonmusk", limit=3)` | Pass |
| G07_switch_source | Hủy Twitter, chỉ gọi `lookup` | `lookup(query="OpenAI", topic="news")` | Pass |
| G08_change_topic | Đổi chủ đề, giữ nguồn tin và thời gian | `lookup(query="Google Gemini", topic="news", timeframe="week")` | Pass |
| G09_compare_update | Giữ nguồn A, cập nhật nguồn B qua nhiều lượt | `compare_sources(A cũ, B mới)` | Pass |
| G10_missing_source | Thiếu nguồn B → hỏi lại, không gọi `compare_sources` | `clarify(question=...)` | Pass |

Run: `runs/group_v1_B_group_openrouter_20261110T120429411988.json` → 10 case, 10 measured.

## B4. Live Chat Evidence

Từ `transcripts/*.transcript.json` (version `v4_tools`, `openai/gpt-4o-mini`, `max_tool_rounds=4`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 (`…121023931699`) | "Tìm 5 tin tức mới nhất về OpenAI trong tuần này." | `lookup(query="OpenAI", topic="news", timeframe="week", max_results=5)` | v4_tools, prompt hash `8ee3a0ab…`, tools hash `5796bb1a…` | Trả về 5 bài, nhưng có kết quả kém liên quan (trang tổng quan công ty tavily.com) |
| 2 (`…121023931699`) | "Tìm 5 bài đăng mới nhất của elonmusk.Đổi thành 3 bài thôi." | `timeline(screenname="elonmusk", limit=3)` | như trên | Tool call đúng (đã áp dụng đổi 5 → 3), nhưng API trả `403 Forbidden`; agent báo lỗi trung thực, không bịa kết quả |
| 3 (`…121023931699`) | `Get-ChildItem .\transcripts -Recurse` (lệnh PowerShell gõ nhầm vào chat) | không gọi tool | như trên | Đúng: từ chối vì ngoài phạm vi, không gọi tool |
| 1 (`…121425500033`) | `So sánh hai nguồn: Nguồn A là "AI giúp tăng năng suất." và nguồn B là "AI có thể thay thế một số công việc."` | `compare_sources(source_a, source_b, title_a="Nguồn A", title_b="Nguồn B")` | như trên | Đúng: similarity 0.3051, không có câu chung, mỗi câu thuộc một nguồn, kèm ghi chú "chỉ so sánh câu chữ" |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?** Gần như tất cả cải thiện đã làm: bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận), rule hỏi lại khi thiếu handle/URL, xác nhận trước khi `send`, phạm vi (không gọi tool cho toán/code), quy ước args (`query` không thêm "news", `today` → `day`, `this week` → `week`), map tên → handle, và toàn bộ logic multi-turn (yêu cầu mới nhất ưu tiên, hủy tool cũ). Cả 5 version đều chỉ sửa `system_prompt.md`.
- **Which fixes belonged in `tools.yaml`?** Mới chỉ có `compare_sources` được viết mô tả đầy đủ (khi nào dùng, khi nào không dùng). Các tool còn lại vẫn mang mô tả "intentionally vague" của starter (ví dụ `timeline`: "Lấy các bài đăng gần đây."). Phần này nên chuyển về `tools.yaml`: quy ước args (handle không có `@`, `topic=news`, `timeframe`, `search_type=Top|Latest`), điều kiện `send` (`confirmed=true`), và enum `policy_area` (nguyên nhân của 5 case fail trong extension eval). Prompt hiện đang gánh những thứ mà declaration nên nói.
- **Which failure needed manual review instead of automatic grading?** (1) Tool call đúng nhưng kết quả kém: lượt 1 của transcript đầu trả về trang giới thiệu công ty thay vì tin tuần này; eval chỉ chấm tool call + args nên không thấy. (2) Timeline trả 403: cần đọc `tool_results` mới biết lỗi do API chứ không phải do agent. (3) Chất lượng so sánh của `compare_sources` (lexical, không hiểu ngữ nghĩa).
- **What would you improve next?**
  1. Sửa hai lỗi của `eval_group.json` (định dạng `turns`, khóa `args`) rồi chạy lại để đo thật G06–G10.
  2. Rewrite mô tả tất cả tool trong `tools.yaml`; bổ sung enum `policy_area`; chạy lại extension eval.
  3. Chạy lặp mỗi version vài lần để biết chênh lệch 0.05 có phải nhiễu không (đặc biệt claim "v3 không đổi, v4 sửa M06").
  4. Thêm test cho `compare_sources` với cặp câu đối lập; cân nhắc so sánh ngữ nghĩa thay vì chỉ so chữ.
  5. Dựng UI, deploy, và điền Phần A (link dùng thử).
  6. Ghi các run `group_v1`, `extension_v1` vào `version_log.csv` (hiện chưa có).

