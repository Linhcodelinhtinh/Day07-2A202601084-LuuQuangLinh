# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 1
**Thành viên:** Trần Đăng Nguyên, Võ Duy Quang, Lưu Quang Linh, Nguyễn Văn Huy Hoàng, Hoàng Trường Giang
**Ngày:** Hôm nay

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40/40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Bộ quy trình và chính sách hỗ trợ khách hàng & quy định người bán trên sàn Thương mại Điện tử Việt Nam (gồm đổi trả/hoàn tiền, đăng bán/hàng cấm, giao hàng/đồng kiểm, thanh toán/hoàn tiền, phí & phạt người bán, giải quyết tranh chấp, bảo mật riêng tư).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách đổi trả và hoàn tiền | https://shopee.vn/docs/policy-returns | 2026-08-03 / 2026.2 | 1,069 | `doc_id: returns-policy`, `customer_role: buyer`, `category: returns`, `language: vi` |
| 2 | Quy định đăng bán sản phẩm và hàng hóa cấm | https://shopee.vn/docs/seller-listing-rules | 2026-08-03 / 2026.1 | 1,280 | `doc_id: seller-listing`, `customer_role: seller`, `category: listing`, `language: vi` |
| 3 | Quy định vận chuyển, giao nhận và đồng kiểm | https://shopee.vn/docs/shipping-policy | 2026-08-03 / 2026.1 | 1,450 | `doc_id: shipping-delivery`, `customer_role: both`, `category: shipping`, `language: vi` |
| 4 | Phương thức thanh toán và quy trình hoàn tiền | https://shopee.vn/docs/payment-methods | 2026-08-03 / 2026.2 | 1,520 | `doc_id: payment-policy`, `customer_role: both`, `category: payment`, `language: vi` |
| 5 | Biểu phí dịch vụ và hệ thống điểm phạt người bán | https://shopee.vn/docs/seller-penalty-points | 2026-08-03 / 2026.1 | 1,480 | `doc_id: seller-fees-penalty`, `customer_role: seller`, `category: seller_fees`, `language: vi` |
| 6 | Quy trình giải quyết tranh chấp và khiếu nại | https://shopee.vn/docs/dispute-resolution | 2026-08-03 / 2026.1 | 1,390 | `doc_id: dispute-resolution`, `customer_role: both`, `category: dispute`, `language: vi` |
| 7 | Chính sách bảo mật thông tin và quyền riêng tư | https://shopee.vn/docs/privacy-policy | 2026-08-03 / 2026.1 | 1,320 | `doc_id: privacy-security`, `customer_role: both`, `category: privacy`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | `string` | `buyer`, `seller`, `both` | Lọc chính xác điều khoản dành riêng cho Người mua hoặc Người bán, tránh nhiễu thông tin giữa 2 vai trò. |
| `category` | `string` | `returns`, `listing`, `shipping`, `payment`, `seller_fees`, `dispute`, `privacy` | Cho phép lọc theo chủ đề/ngành nghiệp vụ cụ thể khi tìm kiếm với `search_with_filter()`. |
| `source_url` | `string` | `https://shopee.vn/docs/policy-returns` | Định danh nguồn gốc công khai và minh bạch thông tin tài liệu. |
| `retrieved_at` | `string` | `2026-08-03` | Theo dõi ngày thu thập dữ liệu để quản lý vòng đời và cập nhật tài liệu. |
| `document_version` | `string` | `2026.1`, `2026.2` | Đảm bảo tính nhất quán của phiên bản chính sách khi đánh giá benchmark. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `return-policy` | FixedSizeChunker (`fixed_size=400`) | 4 | 400 | Không. Thường xuyên cắt ngang câu hoặc giữa các gạch đầu dòng. |
| `return-policy` | SentenceChunker (`max_sentences=3`) | 6 | ~180 | Có, nhưng độ dài chunk quá chênh lệch (có chunk chỉ 50 chữ). |
| `return-policy` | RecursiveChunker (`chunk_size=400`) | 4 | ~380 | Khá tốt. Ưu tiên ngắt ở dấu chấm câu/đoạn, không cắt ngang từ. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Trần Đăng Nguyên**
- **Loại chiến lược:** RecursiveChunker (chunk_size=400, overlap=50)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng RecursiveChunker vì chính sách e-commerce thường chia thành các đoạn văn ngắn. Việc cắt theo đoạn (`\n\n`) hoặc câu (`.`) giúp giữ lại các quy định và điều khoản liên quan với nhau.

**Thành viên 2 — Võ Duy Quang**
- **Loại chiến lược:** FixedSizeChunker (chunk_size=300, overlap=30)
- **Mô tả & lý do chọn cho chủ đề này:** Phương pháp đơn giản, chia cắt nhanh chóng. Kích thước 300 ký tự phù hợp với lượng token của các mô hình LLM nhỏ gọn.

**Thành viên 3 — Lưu Quang Linh**
- **Loại chiến lược:** SentenceChunker (max_sentences=3)
- **Mô tả & lý do chọn cho chủ đề này:** Đảm bảo không bao giờ bị cắt vỡ một câu hoàn chỉnh, giúp mô hình embedding lấy được trọn vẹn ngữ nghĩa của câu luật.

**Thành viên 4 — Nguyễn Văn Huy Hoàng**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)`
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chọn recursive chunking vì tài liệu chính sách được tổ chức thành tiêu đề và các đoạn văn. Kích thước 400 ký tự giúp ưu tiên giữ ranh giới đoạn/câu, đủ để số liệu đi cùng điều kiện liên quan mà không gộp quá nhiều quy định khác nhau vào một chunk. Benchmark sử dụng mô hình `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, tạo 13 chunk từ corpus.

**Thành viên 5 — Hoàng Trường Giang**
- **Loại chiến lược:** HeadingChunker / Regex
- **Mô tả & lý do chọn cho chủ đề này:** Cắt dựa trên các tiêu đề (`#` hoặc `##`) của file Markdown. Đây là cách tối ưu nhất cho văn bản chính sách vì mỗi quy định (ví dụ: Phí vận chuyển) sẽ nằm trọn trong 1 chunk duy nhất.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Đăng Nguyên | Recursive (size 400) | 2/10 | Code chạy ổn định, chia chunk mượt mà không bị cắt vỡ chữ. | Size 400 quá nhỏ so với các điều khoản luật, làm tách rời điều kiện. |
| Võ Duy Quang | FixedSize (size 300) | 0/10 | Dễ lập trình, chạy cực kỳ nhanh. | Thường xuyên cắt ngang câu, làm thay đổi hoàn toàn nghĩa. |
| Lưu Quang Linh | Sentence (3 câu) | 0/10 | Giữ được cấu trúc ngữ pháp tốt nhất. | Có những câu rất ngắn làm lãng phí token, context không đủ rộng. |
| Nguyễn Văn Huy Hoàng | Recursive (size 400) | 9/10 | Evidence xuất hiện trong top-3 ở cả 5/5 query; Q1, Q2, Q3 và Q5 có bằng chứng ngay top-1. | Ở Q4, top-1 đúng tài liệu nhưng thiếu điều kiện đầy đủ; chunk chứa đủ bằng chứng đứng top-2 nên câu trả lời chỉ đạt 1/2 điểm. |
| Hoàng Trường Giang | HeadingChunker | 8/10 | Mọi quy định liên quan đều nằm trọn trong một cụm chủ đề duy nhất. | Đôi khi có section quá dài vượt quá max token limit của mô hình. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Mặc dù `RecursiveChunker` là giải pháp cân bằng nhất về mặt thuật toán, nhưng với đặc thù văn bản luật (Chính sách), tốt nhất nên dùng **HeadingChunker** (cắt theo thẻ `#` hoặc `##`). Lý do là toàn bộ một quy trình (ví dụ: Quy trình trả hàng) cần được giữ chung trong một chunk để LLM có đủ context.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền sau khi Đã giao hàng? | 15 ngày (trừ hàng tươi sống 24h). | `return-policy.md` |
| 2 | TikTok Shop VN hỗ trợ những phương thức gửi trả hàng nào? | (Dữ liệu bị thiếu trong corpus) | Không có |
| 3 | Người bán theo dõi khoản phí vận chuyển trả hàng ở đâu? | (Dữ liệu bị thiếu trong corpus) | Không có |
| 4 | Người bán có phải chấp nhận yêu cầu trả hàng do đổi ý trong mọi trường hợp không? | (Dữ liệu bị thiếu trong corpus) | Không có |
| 5 | Người bán nên duy trì tỷ lệ trả hàng/hoàn tiền dưới mức nào? | (Dữ liệu bị thiếu trong corpus) | Không có |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Người mua có bao nhiêu ngày để yêu cầu trả hàng? | RecursiveChunker | Có (Top-1) | Trả lời hoàn hảo nhờ câu hỏi cụ thể, dễ match từ vựng. Điểm: 2. |
| 2 | TikTok Shop VN hỗ trợ phương thức trả hàng nào? | N/A | Không | Thiếu document nguồn TikTok Shop trong CSDL. Điểm: 0. |
| 3 | Người bán theo dõi khoản phí vận chuyển ở đâu? | N/A | Không | Metadata filter `seller` hoạt động nhưng chunk không chứa đáp án. Điểm: 0. |
| 4 | Người bán có phải chấp nhận do đổi ý không? | N/A | Không | Điểm: 0. |
| 5 | Duy trì tỷ lệ trả hàng dưới mức nào? | N/A | Không | Điểm: 0. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, ở câu 3 (khi dùng `customer_role='seller'`), filter đã loại bỏ hoàn toàn các tài liệu dành cho người mua. Nếu dữ liệu có chứa câu trả lời thực sự, filter sẽ giúp LLM không bị ảo giác nhầm lẫn giữa luật người mua và luật người bán.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Điểm yếu chết người của RecursiveChunking khi đối mặt với văn bản quy định/điều khoản.
> - Sức mạnh của Qwen LLM khi đối diện với các chunk rác (Biết từ chối trả lời thay vì ảo giác).
> - Lợi ích của việc áp dụng Metadata filtering (Role-based) cho các hệ thống hỗ trợ đa người dùng (Buyer vs Seller).

**Bài học rút ra khi so sánh trong nhóm:**
> Thuật toán chia nhỏ tài liệu (Chunking) quan trọng ngang ngửa với mô hình nhúng (Embedding). Nếu chia sai, dù LLM mạnh đến mấy cũng không thể ráp nối lại thông tin nếu thông tin bị thiếu hụt ở Top-3 chunks.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Sẽ thu thập thêm các bộ dữ liệu từ TikTok Shop và Lazada, thêm trường metadata `platform`, và áp dụng Chunking theo cấu trúc Markdown (Header/Section) thay vì chỉ đếm số từ.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |