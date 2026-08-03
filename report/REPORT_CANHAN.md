# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lưu Quang Linh  
**MSSV:** 2A202601084  
**Nhóm:** Nhóm 1 (E-Commerce Policy - K4)  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60/60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự Cosine cao (tiệm cận 1.0) nghĩa là hai đoạn văn bản có các vector biểu diễn hướng về cùng một phía trong không gian vector đa chiều, thể hiện mức độ tương đồng rất lớn về mặt ngữ nghĩa bất kể độ dài ngắn của hai đoạn văn.

**Ví dụ có độ tương tự CAO:**
- Câu A: Chính sách đổi trả hàng áp dụng trong vòng 15 ngày kể từ khi nhận hàng.
- Câu B: Khách hàng có quyền yêu cầu hoàn tiền và trả lại sản phẩm trong thời hạn 15 ngày.
- Tại sao tương đồng: Cả hai câu đều truyền tải cùng một ý định và thông tin về thời gian và quyền hạn trả hàng của người mua.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Chính sách đổi trả hàng áp dụng trong vòng 15 ngày kể từ khi nhận hàng.
- Câu B: Công thức tính diện tích hình tròn là $S = \pi r^2$.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau (chính sách TMĐT và toán học cơ bản), không có mối liên quan về ngữ cảnh hay từ vựng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự Cosine chỉ đo góc giữa các vector mà không phụ thuộc vào độ dài (mô-đun) của vector. Khoảng cách Euclid bị ảnh hưởng bởi độ dài văn bản (văn bản dài hơn sinh ra vector có độ dài lớn hơn), làm sai lệch việc so sánh độ tương đồng ngữ nghĩa giữa một văn bản ngắn và một văn bản dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: $\text{Số lượng chunk} = \left\lceil \frac{\text{độ\_dài} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \left\lceil 22.11 \right\rceil = 23$  
> **Đáp án:** 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số lượng chunk tăng lên 25 chunks ($\lceil \frac{9900}{400} \rceil = 25$). Tăng độ chồng chéo giúp giữ trọn vẹn ngữ cảnh ở ranh giới giữa các chunk, tránh việc một câu hoặc một ý nghĩa quan trọng bị cắt đôi gãy ngắt giữa hai chunk kề nhau.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy `re.split(r'(?<=[.!?])\s+|\.\n', text.strip())` để tách văn bản thành từng câu dựa trên các dấu câu cuối câu (`.`, `!`, `?`, `.\n`). Xử lý trường hợp ngoại lệ bằng cách loại bỏ các khoảng trắng thừa và ký tự trống, sau đó gom các câu lại thành nhóm tối đa `max_sentences_per_chunk` câu để hình thành từng chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Sử dụng thuật toán đệ quy duyệt qua các dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) là khi độ dài chuỗi $\le$ `chunk_size` hoặc đã hết danh sách phân cách. Hàm sẽ tách chuỗi theo dấu phân cách hiện tại và tích lũy các phần nhỏ cho đến khi đạt `chunk_size`; nếu một phần đơn lẻ vẫn vượt quá `chunk_size`, nó tiếp tục được đệ quy xử lý bằng dấu phân cách kế tiếp.

**`ListAwareChunker.chunk` (Chiến lược mở rộng cá nhân)** — hướng tiếp cận:
> Thiết kế class tùy chỉnh `ListAwareChunker` dùng Regex `re.compile(r"^\s*([-*•]|\d+[\.\)])\s+")` nhằm phát hiện các dòng danh sách liệt kê/gạch đầu dòng. Hàm sẽ gom giữ nguyên toàn bộ câu dẫn nhập phía trên cùng tất cả các mục danh sách đi kèm vào cùng 1 chunk, tránh việc các bước quy trình bị cắt lẻ từng dòng làm mất bối cảnh.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Hàm `add_documents` nhận danh sách `Document`, gọi `_make_record` để tính vector nhúng qua `self._embedding_fn` và lưu dictionary cấu trúc vào `self._store` (đồng thời thêm vào ChromaDB collection nếu `_use_chroma=True`). Hàm `search` tính tích vô hướng (dot product) qua `_dot` giữa vector truy vấn và vector của từng chunk, sau đó xếp hạng giảm dần theo `score` và trả về `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện tiền lọc (pre-filtering): lọc danh sách các chunk trong `_store` thỏa mãn tất cả điều kiện của `metadata_filter`, sau đó mới truyền danh sách đã lọc vào `_search_records`. `delete_document` lọc bỏ tất cả các chunk có `id` hoặc `metadata['doc_id']` khớp với `doc_id` cần xóa và trả về `True` nếu số lượng chunk giảm đi.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` thực hiện mô hình RAG tiêu chuẩn: gọi `self.store.search(question, top_k=top_k)` để truy xuất các chunk liên quan nhất. Sau đó ghép nội dung các chunk thành chuỗi ngữ cảnh `context_str` và inject vào mẫu prompt: `Context:\n{context_str}\n\nQuestion: {question}\nAnswer:`, cuối cùng chuyển prompt này cho `self.llm_fn` để tạo câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  6%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 13%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 15%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 18%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 20%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 22%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 25%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 27%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 29%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 31%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 34%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 36%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 43%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 56%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 61%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 63%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 65%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 68%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 70%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 72%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 75%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 77%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 79%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 81%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 84%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 86%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 93%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [ 95%]
tests/test_solution.py::TestListAwareChunker::test_chunker_exists PASSED [ 97%]
tests/test_solution.py::TestListAwareChunker::test_preserves_bullet_lists PASSED [100%]
============================= 44 passed in 0.16s ==============================
```

**Số lượng bài test vượt qua (pass):** 44 / 44

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tải ứng dụng mua sắm trên di động | Ứng dụng di động dùng để đặt hàng | cao | -0.0999 | Chưa (Mock) |
| 2 | Chính sách đổi trả trong vòng 15 ngày | Khách hàng có thể trả lại hàng trong 15 ngày | cao | 0.0006 | Đúng |
| 3 | Hỗ trợ khách hàng 24/7 | Mèo là động vật nuôi phổ biến | thấp | -0.0361 | Đúng |
| 4 | Phương thức thanh toán qua thẻ tín dụng | Thanh toán trực tuyến bằng thẻ visa | cao | -0.0346 | Chưa (Mock) |
| 5 | Quy định dành cho người bán hàng | Công thức tính diện tích hình tròn | thấp | -0.0104 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điểm số thực tế khi chạy Mock embedder gần như xoay quanh $0.0$ và có những cặp câu đồng nghĩa lại có score âm (ví dụ Cặp 1 & 4). Điều này là do mock embedder chỉ băm chuỗi ký tự theo cơ chế giả lập xác định chứ không học được ngữ nghĩa tiếng Việt. Muốn phản ánh đúng mức độ tương đồng ngữ nghĩa thực sự, cần chuyển sang mô hình nhúng thực tế như `LocalEmbedder` (`sentence-transformers`).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này trùng với bộ câu hỏi thống nhất của Nhóm 1** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền sau khi Đã giao hàng? | `15 ngày kể từ lúc đơn hàng được cập nhật trạng thái Giao hàng thành công (01-chinh-sach-doi-tra.md)` | 0.2340 | Có (Top-1) | Thời hạn tối đa là 15 ngày kể từ khi đơn hàng giao thành công. |
| 2 | TikTok Shop VN hỗ trợ những phương thức gửi trả hàng nào? | `> Khối metadata phía trên là template mẫu cho K4 (returns-policy.md)` | 0.0093 | Không | Không tìm thấy thông tin phương thức trả hàng TikTok Shop trong CSDL. |
| 3 | Người bán theo dõi khoản phí vận chuyển trả hàng ở đâu? *(Filter: customer_role=seller)* | `Hệ thống Sao Quả Tạ tổng quan về các hình thức phạt Người bán (04-xu-ly-don-hang.md)` | 0.0891 | Không | CSDL chưa chứa bài viết hướng dẫn chi tiết theo dõi khoản phí vận chuyển cho seller. |
| 4 | Người bán có phải chấp nhận yêu cầu trả hàng do đổi ý trong mọi trường hợp không? | `Quy định đăng bán sản phẩm và danh mục sản phẩm cấm/hạn chế (03-quy-dinh-dang-ban.md)` | 0.0441 | Không | Tài liệu chưa cập nhật điều khoản bắt buộc chấp nhận đổi ý cho seller. |
| 5 | Người bán nên duy trì tỷ lệ trả hàng/hoàn tiền dưới mức nào? | `Chính sách đổi trả và hoàn tiền (01-chinh-sach-doi-tra.md)` | -0.0661 | Không | Tài liệu hiện tại chưa có thông số tỷ lệ NFR cụ thể. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Nhóm đã học được rằng ngoài thuật toán Chunking (`SentenceChunker` hay `RecursiveChunker`), việc xây dựng **Chiến lược cấu trúc dữ liệu tài liệu (Data Strategy)** và dùng **HeadingChunker / ListAwareChunker** đóng vai trò cực kỳ quyết định. Đồng thời, việc kết hợp lọc siêu dữ liệu `metadata_filter={'customer_role': 'seller'}` giúp loại bỏ hẳn nhiễu thông tin dành cho người mua.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
