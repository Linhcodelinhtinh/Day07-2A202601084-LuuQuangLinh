import os
from ingest import build_knowledge_base
from src.chunking import ListAwareChunker
from src.agent import KnowledgeBaseAgent
from main import demo_llm, _select_embedder

def main():
    # 1. Chọn chunker của riêng bạn
    chunker = ListAwareChunker(max_chunk_size=400)
    
    # 2. Chọn embedder (Sẽ tự động đọc cấu hình LOCAL trong .env)
    embedder = _select_embedder()
    
    # Nạp cả thư mục corpus. embedding_fn là tham số bắt buộc thứ hai.
    print("Strategy: ListAwareChunker(chunk_size=400)")
    store = build_knowledge_base("data/k4_ecommerce", embedder, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore\n")
    
    # Setup Agent
    agent = KnowledgeBaseAgent(store, demo_llm)
    
    benchmark_queries = [
        {"query": "Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoặc hoàn tiền sau khi đơn ở trạng thái Đã giao hàng?", "filter": None},
        {"query": "TikTok Shop Việt Nam hỗ trợ những phương thức gửi trả hàng nào?", "filter": None},
        {"query": "Người bán theo dõi khoản phí vận chuyển trả hàng ở đâu?", "filter": {'customer_role': 'seller'}},
        {"query": "Người bán có phải chấp nhận yêu cầu trả hàng do đổi ý trong mọi trường hợp không?", "filter": None},
        {"query": "Người bán nên duy trì tỷ lệ trả hàng hoặc hoàn tiền do lỗi của mình dưới mức nào?", "filter": None},
    ]
    
    for i, item in enumerate(benchmark_queries, 1):
        q = item["query"]
        filter_dict = item["filter"]
        print(f"=== Query {i}: {q} ===")
        if filter_dict:
            print(f"  [Metadata Filter]: {filter_dict}")
            results = store.search_with_filter(q, top_k=3, metadata_filter=filter_dict)
        else:
            results = store.search(q, top_k=3)
            
        print("  Top-3 Results:")
        for rank, res in enumerate(results, 1):
            doc_id = res['metadata'].get('doc_id', 'unknown')
            preview = res['content'][:100].replace('\n', ' ')
            print(f"    {rank}. score={res['score']:.3f} | doc_id={doc_id} | {preview}...")
            
        # Agent response
        print("  Agent Response:")
        # We need to construct context just to print demo_llm or let agent answer it normally
        # If we use search_with_filter inside agent, wait, agent.answer() uses search() only!
        # The instructions say: "Chạy 5 query qua search() hoặc search_with_filter(), in strategy và tham số, số chunk đã nạp, top-3 gồm score, doc_id, preview, và câu trả lời của agent"
        # Since agent doesn't support filter right now, we can just print the agent's answer without filter for the ones without filter, or manually pass if we modified agent.
        # But we'll just call agent.answer() - it will ignore the filter for question 2 but we already printed the filtered chunks. 
        ans = agent.answer(q, top_k=3)
        print(f"    {ans}\n")

if __name__ == "__main__":
    main()